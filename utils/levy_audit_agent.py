"""
Levy Audit Agent Implementation for the Levy Calculation System.

This module provides the "Lev" AI agent, an expert in property tax and levy auditing,
which assists users in understanding, auditing, and optimizing levy processes.
The agent provides:
- Levy compliance verification
- Expert property tax law guidance
- Contextual recommendations for levy optimization
- Natural language explanations of complex levy concepts
- Historical, current, and potential future levy law insights
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple, cast

from utils.anthropic_utils import get_claude_service, check_api_key_status
from utils.sanitize_utils import sanitize_html, sanitize_mcp_insights
from utils.mcp_agents import MCPAgent
from utils.mcp_core import registry
from utils.html_sanitizer import sanitize_html, sanitize_mcp_insights
from utils.api_logging import APICallRecord, api_tracker

logger = logging.getLogger(__name__)

class LevyAuditAgent(MCPAgent):
    """
    Advanced AI agent specialized in levy auditing and property tax expertise.
    
    This agent extends the base MCPAgent with specialized capabilities for:
    - Levy compliance verification against local, state, and federal requirements
    - Historical and current property tax law expertise
    - Contextual recommendations for levy optimization and compliance
    - Interactive auditing workflow assistance
    - Natural language explanations of complex levy concepts
    """
    
    def __init__(self):
        """Initialize the Levy Audit Agent."""
        super().__init__(
            name="Lev",
            description="World's foremost expert in property tax and levy auditing"
        )
        
        # Register specialized capabilities
        self.register_capability("audit_levy_compliance")
        self.register_capability("explain_levy_law")
        self.register_capability("provide_levy_recommendations")
        self.register_capability("process_levy_query")
        self.register_capability("verify_levy_calculation")
        self.register_capability("audit_data_quality")
        self.register_capability("analyze_levy_trends")
        
        # Claude service for AI capabilities
        self.claude = get_claude_service()
        
        # Conversation history for multi-turn dialogue
        self.conversation_history = []
        
    def audit_levy_compliance(self, 
                            district_id: str,
                            year: int,
                            full_audit: bool = False) -> Dict[str, Any]:
        """
        Audit a tax district's levy for compliance with applicable laws.
        
        Args:
            district_id: Tax district identifier
            year: Assessment year
            full_audit: Whether to perform a comprehensive audit (more detailed)
            
        Returns:
            Compliance audit results with findings and recommendations
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "audit_results": "Levy compliance audit not available"
            }
        
        # Get district information from the registry
        district_info = registry.execute_function(
            "get_district_details",
            {"district_id": district_id}
        )
        
        # Get levy data for the specified year
        levy_data = registry.execute_function(
            "get_district_levy_data",
            {"district_id": district_id, "year": year}
        )
        
        # Get historical rates for context
        historical_rates = registry.execute_function(
            "get_district_historical_rates",
            {"district_id": district_id, "years": 5}  # Last 5 years for context
        )
        
        # Determine the appropriate compliance rules to check
        district_type = district_info.get("district_type", "UNKNOWN")
        state = district_info.get("state", "WA")  # Default to Washington state
        
        # Set up the audit prompt based on the district details
        audit_depth = "comprehensive" if full_audit else "standard"
        
        prompt = f"""
        As Lev, the world's foremost expert in property tax and levy auditing, perform a {audit_depth} 
        compliance audit for the following tax district's levy data for {year}.
        
        District Information:
        {json.dumps(district_info, indent=2)}
        
        Levy Data for {year}:
        {json.dumps(levy_data, indent=2)}
        
        Historical Rates (for context):
        {json.dumps(historical_rates, indent=2)}
        
        Please perform a thorough compliance analysis considering:
        1. Applicable {state} state laws for {district_type} tax districts
        2. Federal requirements that may apply
        3. Local ordinances and special provisions
        4. Levy rate limits and statutory caps
        5. Year-over-year increase restrictions
        6. Special exemptions or circumstances
        7. Procedural compliance requirements
        
        For each finding, indicate:
        - The specific compliance issue or confirmation
        - The relevant statute or regulation
        - The severity level (Critical, High, Medium, Low, or Compliant)
        - Specific recommendation for addressing any issues
        
        Format your response as JSON with the following structure:
        {{
            "district_name": "{district_info.get('name', 'Unknown District')}",
            "audit_year": {year},
            "audit_type": "{audit_depth}",
            "compliance_summary": "string",
            "compliance_score": "percentage as float",
            "findings": [
                {{
                    "area": "string",
                    "status": "Critical|High|Medium|Low|Compliant",
                    "finding": "string",
                    "regulation": "string",
                    "recommendation": "string"
                }},
                // More findings...
            ],
            "overall_recommendations": ["string", "string", ...],
            "potential_risks": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to generate the compliance audit
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully generated levy compliance audit for district {district_id}, year {year}")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "error": "Failed to process audit results",
                "district_name": district_info.get("name", "Unknown District"),
                "audit_year": year,
                "audit_type": audit_depth,
                "compliance_summary": "Audit processing error",
                "compliance_score": 0.0,
                "findings": [],
                "overall_recommendations": [
                    "Please try running the audit again",
                    "Contact system administrator if the problem persists"
                ],
                "potential_risks": [
                    "Audit failed to complete - compliance status unknown"
                ]
            }
        except Exception as e:
            logger.error(f"Error in levy compliance audit: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def explain_levy_law(self, 
                       topic: str,
                       jurisdiction: str = "WA", 
                       level_of_detail: str = "standard") -> Dict[str, Any]:
        """
        Provide expert explanation of property tax and levy laws.
        
        Args:
            topic: The specific levy or tax law topic to explain
            jurisdiction: State or jurisdiction code (default: WA for Washington)
            level_of_detail: Level of detail for the explanation (basic, standard, detailed)
            
        Returns:
            Detailed explanation with relevant citations and practical implications
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "explanation": "Levy law explanation not available"
            }
        
        # Convert level of detail to appropriate depth
        detail_level_map = {
            "basic": "a concise overview accessible to non-specialists",
            "standard": "a comprehensive explanation with key details",
            "detailed": "an in-depth analysis with extensive citations and nuances"
        }
        detail_level = detail_level_map.get(level_of_detail.lower(), "a comprehensive explanation with key details")
        
        prompt = f"""
        As Lev, the world's foremost expert in property tax and levy laws, provide {detail_level}
        of '{topic}' under {jurisdiction} jurisdiction.
        
        Include in your explanation:
        1. The fundamental purpose and principles of this aspect of levy law
        2. Relevant statutory references and citations
        3. How this applies in practice for tax districts and property owners
        4. Common misconceptions or areas of confusion
        5. Recent developments or changes to be aware of
        6. Practical implications for levy calculation and administration
        
        Format your response as JSON with the following structure:
        {{
            "topic": "{topic}",
            "jurisdiction": "{jurisdiction}",
            "overview": "string",
            "key_principles": ["string", "string", ...],
            "statutory_references": ["string", "string", ...],
            "practical_applications": ["string", "string", ...],
            "common_misconceptions": ["string", "string", ...],
            "recent_developments": ["string", "string", ...],
            "see_also": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to generate the explanation
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully generated levy law explanation for topic: {topic}")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "topic": topic,
                "jurisdiction": jurisdiction,
                "overview": "Error processing explanation request",
                "key_principles": [],
                "statutory_references": [],
                "practical_applications": [],
                "common_misconceptions": [],
                "recent_developments": [],
                "see_also": []
            }
        except Exception as e:
            logger.error(f"Error generating levy law explanation: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def provide_levy_recommendations(self,
                                  district_id: str,
                                  year: int,
                                  focus_area: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate contextual recommendations for levy optimization and compliance.
        
        Args:
            district_id: Tax district identifier 
            year: Assessment year
            focus_area: Specific area of focus (compliance, optimization, public communication)
            
        Returns:
            Tailored recommendations with justifications and priority levels
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "recommendations": []
            }
        
        # Get district information from the registry
        district_info = registry.execute_function(
            "get_district_details",
            {"district_id": district_id}
        )
        
        # Get levy data for the specified year
        levy_data = registry.execute_function(
            "get_district_levy_data",
            {"district_id": district_id, "year": year}
        )
        
        # Get historical rates for context
        historical_rates = registry.execute_function(
            "get_district_historical_rates",
            {"district_id": district_id, "years": 5}  # Last 5 years for context
        )
        
        # Determine focus areas based on input
        if not focus_area:
            focus_areas = ["compliance", "optimization", "communication"]
        else:
            focus_areas = [focus_area]
        
        prompt = f"""
        As Lev, the world's foremost expert in property tax and levy optimization, analyze the 
        following tax district data and provide strategic recommendations focused on {', '.join(focus_areas)}.
        
        District Information:
        {json.dumps(district_info, indent=2)}
        
        Levy Data for {year}:
        {json.dumps(levy_data, indent=2)}
        
        Historical Rates (for context):
        {json.dumps(historical_rates, indent=2)}
        
        Based on this data, provide:
        1. Strategic recommendations for improving levy {', '.join(focus_areas)}
        2. Data-driven justification for each recommendation
        3. Priority level and potential impact of each recommendation
        4. Implementation considerations and potential challenges
        
        Format your response as JSON with the following structure:
        {{
            "district_name": "{district_info.get('name', 'Unknown District')}",
            "assessment_year": {year},
            "focus_areas": {json.dumps(focus_areas)},
            "executive_summary": "string",
            "recommendations": [
                {{
                    "title": "string",
                    "description": "string",
                    "justification": "string",
                    "focus_area": "compliance|optimization|communication",
                    "priority": "critical|high|medium|low",
                    "implementation_considerations": "string"
                }},
                // More recommendations...
            ],
            "additional_insights": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to generate recommendations
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully generated levy recommendations for district {district_id}")
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "district_name": district_info.get("name", "Unknown District"),
                "assessment_year": year,
                "focus_areas": focus_areas,
                "executive_summary": "Error processing recommendation request",
                "recommendations": [],
                "additional_insights": []
            }
        except Exception as e:
            logger.error(f"Error generating levy recommendations: {str(e)}")
            return {"error": sanitize_html(str(e))}
    
    def process_levy_query(self,
                         query: str,
                         context: Optional[Dict[str, Any]] = None,
                         add_to_history: bool = True) -> Dict[str, Any]:
        """
        Process a natural language query about levy and property tax topics.
        
        Args:
            query: Natural language query
            context: Additional context for the query (district, year, etc.)
            add_to_history: Whether to add this interaction to conversation history
            
        Returns:
            Response to the natural language query with relevant explanations
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "response": "Query processing not available"
            }
        
        # Add query to conversation history if enabled
        if add_to_history:
            self.conversation_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
        
        # Prepare context for the query
        context_data = ""
        if context:
            context_data = f"Context Information:\n{json.dumps(context, indent=2)}\n\n"
        
        # Include relevant conversation history for continuity
        history_text = ""
        if self.conversation_history and len(self.conversation_history) > 1:
            history_text = "Previous conversation:\n"
            for i, entry in enumerate(self.conversation_history[:-1]):
                history_text += f"{entry['role'].title()}: {entry['content']}\n"
            history_text += "\n"
        
        prompt = f"""
        As Lev, the world's foremost expert in property tax and levy laws, respond to the following query:
        
        {history_text}
        {context_data}
        User Query: {query}
        
        Provide a comprehensive answer that demonstrates your deep expertise in property tax systems, levy laws,
        and assessment procedures. Include:
        
        1. A direct answer to the query
        2. Relevant citations or references if applicable
        3. Practical implications and considerations
        4. Any relevant historical context or future developments
        5. Follow-up suggestions that might be useful
        
        Format your response as JSON with the following structure:
        {{
            "query": "{query}",
            "answer": "string",
            "citations": ["string", "string", ...],
            "practical_implications": ["string", "string", ...],
            "additional_context": "string",
            "follow_up_questions": ["string", "string", ...]
        }}
        """
        
        try:
            # Use Claude to process the query
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully processed levy query: {query[:50]}...")
            
            # Add response to conversation history if enabled
            if add_to_history:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "query": query,
                "answer": "I'm sorry, but I couldn't properly process your query about levy or property tax. Please try rephrasing your question.",
                "citations": [],
                "practical_implications": [],
                "additional_context": "",
                "follow_up_questions": [
                    "Could you rephrase your question about the levy process?",
                    "Would you like information about a specific aspect of property tax laws?",
                    "Are you looking for information about a particular jurisdiction?"
                ]
            }
        except Exception as e:
            logger.error(f"Error processing levy query: {str(e)}")
            return {"error": sanitize_html(str(e))}
            
    def analyze_levy_trends(self,
                         district_id: Optional[str] = None,
                         tax_code_id: Optional[str] = None, 
                         year_range: Optional[List[int]] = None,
                         trend_type: str = "rate",
                         compare_to_similar: bool = False) -> Dict[str, Any]:
        """
        Analyze historical trends in levy rates and property taxes.
        
        This capability performs time-series analysis on levy data to identify
        patterns, anomalies, and forecasts future trends based on historical data.
        
        Args:
            district_id: Optional tax district ID to focus analysis on
            tax_code_id: Optional tax code ID to focus analysis on
            year_range: List containing start and end years for analysis, e.g. [2018, 2025]
            trend_type: Type of trend analysis - 'rate', 'value', 'revenue', or 'comprehensive'
            compare_to_similar: Whether to compare trends with similar districts/areas
            
        Returns:
            Detailed trend analysis results with visualizable data and insights
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "trend_analysis": "Levy trend analysis not available"
            }
        
        try:
            # Import required modules
            from flask import current_app
            from sqlalchemy import desc, func
            import logging
            from datetime import datetime, timedelta
            import numpy as np
            from models import (
                TaxDistrict, TaxCode, Property, TaxCodeHistoricalRate,
                ImportLog, LevyAuditRecord
            )
            
            # Get database session
            db = current_app.extensions.get('sqlalchemy').db
            
            # Set default year range if not provided (7 years)
            current_year = datetime.now().year
            if not year_range:
                year_range = [current_year - 6, current_year]
            
            start_year, end_year = year_range
            
            # Ensure we have 2 valid years and they're in the right order
            if start_year > end_year:
                start_year, end_year = end_year, start_year
                
            # Limit to reasonable range (max 10 years)
            if (end_year - start_year) > 10:
                end_year = start_year + 10
                
            years = list(range(start_year, end_year + 1))
            
            # Gather trend data based on parameters
            trend_data = {}
            
            # Tax district specific analysis
            if district_id:
                # Get district details
                district = db.session.query(TaxDistrict).filter(
                    TaxDistrict.id == district_id
                ).first()
                
                if not district:
                    return {
                        "error": f"Tax district with ID {district_id} not found",
                        "trend_analysis": {}
                    }
                    
                # Get tax codes associated with this district
                tax_codes = db.session.query(TaxCode).filter(
                    TaxCode.tax_district_id == district_id
                ).all()
                
                tax_code_ids = [tc.id for tc in tax_codes]
                
                # Get historical rates for all tax codes in this district
                historical_rates = db.session.query(TaxCodeHistoricalRate).filter(
                    TaxCodeHistoricalRate.tax_code_id.in_(tax_code_ids),
                    TaxCodeHistoricalRate.year.between(start_year, end_year)
                ).all()
                
                # Organize by year
                yearly_data = {year: [] for year in years}
                for rate in historical_rates:
                    if rate.year in yearly_data:
                        yearly_data[rate.year].append({
                            'tax_code_id': rate.tax_code_id,
                            'levy_rate': rate.levy_rate,
                            'levy_amount': rate.levy_amount,
                            'total_assessed_value': rate.total_assessed_value
                        })
                
                # Calculate district averages per year
                district_trends = []
                for year in years:
                    rates = yearly_data.get(year, [])
                    if rates:
                        avg_rate = sum(r['levy_rate'] for r in rates if r['levy_rate'] is not None) / len(rates)
                        total_levy = sum(r['levy_amount'] for r in rates if r['levy_amount'] is not None)
                        total_value = sum(r['total_assessed_value'] for r in rates if r['total_assessed_value'] is not None)
                    else:
                        avg_rate = None
                        total_levy = None
                        total_value = None
                        
                    district_trends.append({
                        'year': year,
                        'avg_levy_rate': avg_rate,
                        'total_levy_amount': total_levy,
                        'total_assessed_value': total_value,
                        'data_quality': 'high' if rates else 'missing'
                    })
                
                trend_data['district'] = {
                    'id': district.id,
                    'name': district.name,
                    'district_type': district.district_type,
                    'yearly_trends': district_trends
                }
                
                # Get similar districts if requested
                if compare_to_similar:
                    similar_districts = db.session.query(TaxDistrict).filter(
                        TaxDistrict.district_type == district.district_type,
                        TaxDistrict.id != district.id
                    ).limit(5).all()
                    
                    similar_data = []
                    for similar in similar_districts:
                        # Get tax codes for this similar district
                        similar_tax_codes = db.session.query(TaxCode).filter(
                            TaxCode.tax_district_id == similar.id
                        ).all()
                        
                        similar_tax_code_ids = [tc.id for tc in similar_tax_codes]
                        
                        # Get historical rates for similar district
                        similar_historical_rates = db.session.query(TaxCodeHistoricalRate).filter(
                            TaxCodeHistoricalRate.tax_code_id.in_(similar_tax_code_ids),
                            TaxCodeHistoricalRate.year.between(start_year, end_year)
                        ).all()
                        
                        # Organize by year
                        similar_yearly_data = {year: [] for year in years}
                        for rate in similar_historical_rates:
                            if rate.year in similar_yearly_data:
                                similar_yearly_data[rate.year].append({
                                    'levy_rate': rate.levy_rate,
                                    'levy_amount': rate.levy_amount,
                                    'total_assessed_value': rate.total_assessed_value
                                })
                        
                        # Calculate averages per year
                        similar_trends = []
                        for year in years:
                            rates = similar_yearly_data.get(year, [])
                            if rates:
                                avg_rate = sum(r['levy_rate'] for r in rates if r['levy_rate'] is not None) / len(rates)
                                total_levy = sum(r['levy_amount'] for r in rates if r['levy_amount'] is not None)
                                total_value = sum(r['total_assessed_value'] for r in rates if r['total_assessed_value'] is not None)
                            else:
                                avg_rate = None
                                total_levy = None
                                total_value = None
                                
                            similar_trends.append({
                                'year': year,
                                'avg_levy_rate': avg_rate,
                                'total_levy_amount': total_levy,
                                'total_assessed_value': total_value
                            })
                        
                        similar_data.append({
                            'id': similar.id,
                            'name': similar.name,
                            'yearly_trends': similar_trends
                        })
                    
                    trend_data['similar_districts'] = similar_data
            
            # Specific tax code analysis
            elif tax_code_id:
                # Get tax code details
                tax_code = db.session.query(TaxCode).filter(
                    TaxCode.id == tax_code_id
                ).first()
                
                if not tax_code:
                    return {
                        "error": f"Tax code with ID {tax_code_id} not found",
                        "trend_analysis": {}
                    }
                
                # Get historical rates for this tax code
                historical_rates = db.session.query(TaxCodeHistoricalRate).filter(
                    TaxCodeHistoricalRate.tax_code_id == tax_code_id,
                    TaxCodeHistoricalRate.year.between(start_year, end_year)
                ).all()
                
                # Create yearly trend data
                tax_code_trends = []
                for year in years:
                    rate_data = next((r for r in historical_rates if r.year == year), None)
                    
                    tax_code_trends.append({
                        'year': year,
                        'levy_rate': rate_data.levy_rate if rate_data else None,
                        'levy_amount': rate_data.levy_amount if rate_data else None,
                        'total_assessed_value': rate_data.total_assessed_value if rate_data else None,
                        'data_quality': 'high' if rate_data else 'missing'
                    })
                
                # Get district info for context
                district = db.session.query(TaxDistrict).filter(
                    TaxDistrict.id == tax_code.tax_district_id
                ).first()
                
                trend_data['tax_code'] = {
                    'id': tax_code.id,
                    'code': tax_code.code,
                    'district_name': district.name if district else "Unknown District",
                    'yearly_trends': tax_code_trends
                }
            
            # System-wide analysis (no specific district or tax code)
            else:
                # Get aggregated data for all districts by year
                system_trends = []
                
                for year in years:
                    # Get average levy rate across all tax codes for this year
                    avg_rate_query = db.session.query(
                        func.avg(TaxCodeHistoricalRate.levy_rate).label('avg_rate'),
                        func.sum(TaxCodeHistoricalRate.levy_amount).label('total_levy'),
                        func.sum(TaxCodeHistoricalRate.total_assessed_value).label('total_value')
                    ).filter(
                        TaxCodeHistoricalRate.year == year
                    ).first()
                    
                    if avg_rate_query and avg_rate_query.avg_rate is not None:
                        avg_rate = float(avg_rate_query.avg_rate)
                        total_levy = float(avg_rate_query.total_levy) if avg_rate_query.total_levy is not None else None
                        total_value = float(avg_rate_query.total_value) if avg_rate_query.total_value is not None else None
                    else:
                        avg_rate = None
                        total_levy = None
                        total_value = None
                    
                    # Count tax codes with data for this year
                    tax_code_count = db.session.query(func.count(TaxCodeHistoricalRate.id)).filter(
                        TaxCodeHistoricalRate.year == year
                    ).scalar() or 0
                    
                    system_trends.append({
                        'year': year,
                        'avg_levy_rate': avg_rate,
                        'total_levy_amount': total_levy,
                        'total_assessed_value': total_value,
                        'tax_code_count': tax_code_count,
                        'data_quality': 'high' if tax_code_count > 0 else 'missing'
                    })
                
                # Get district type breakdowns
                district_type_averages = {}
                district_types = db.session.query(TaxDistrict.district_type).distinct().all()
                
                for district_type_tuple in district_types:
                    district_type = district_type_tuple[0]
                    
                    # Get districts of this type
                    district_ids = db.session.query(TaxDistrict.id).filter(
                        TaxDistrict.district_type == district_type
                    ).all()
                    district_ids = [d[0] for d in district_ids]
                    
                    # Get tax codes for these districts
                    tax_code_ids = db.session.query(TaxCode.id).filter(
                        TaxCode.tax_district_id.in_(district_ids)
                    ).all()
                    tax_code_ids = [tc[0] for tc in tax_code_ids]
                    
                    # Get historical rates for these tax codes by year
                    type_yearly_trends = []
                    
                    for year in years:
                        avg_rate_query = db.session.query(
                            func.avg(TaxCodeHistoricalRate.levy_rate).label('avg_rate')
                        ).filter(
                            TaxCodeHistoricalRate.tax_code_id.in_(tax_code_ids),
                            TaxCodeHistoricalRate.year == year
                        ).first()
                        
                        if avg_rate_query and avg_rate_query.avg_rate is not None:
                            avg_rate = float(avg_rate_query.avg_rate)
                        else:
                            avg_rate = None
                        
                        type_yearly_trends.append({
                            'year': year,
                            'avg_levy_rate': avg_rate
                        })
                    
                    district_type_averages[district_type] = type_yearly_trends
                
                trend_data['system'] = {
                    'yearly_trends': system_trends,
                    'district_type_trends': district_type_averages
                }
            
            # Add metadata
            metadata = {
                'years_analyzed': years,
                'trend_type': trend_type,
                'analysis_timestamp': datetime.now().isoformat(),
                'comparison_included': compare_to_similar
            }
            
            trend_data['metadata'] = metadata
            
            # Use Claude to analyze the trends
            prompt = f"""
            As Lev, the world's foremost expert in property tax and levy analysis, review the
            following historical trend data and provide detailed insights and analysis.
            
            TREND DATA:
            {json.dumps(trend_data, indent=2)}
            
            Focus your analysis on {"tax code " + str(tax_code_id) if tax_code_id else "district " + str(district_id) if district_id else "system-wide"} 
            {"and comparison with similar districts" if compare_to_similar else ""} trends over {start_year}-{end_year}.
            
            Primarily analyze {trend_type} trends, with special attention to:
            - Long-term patterns and trajectory
            - Year-over-year changes and volatility
            - Anomalies or outliers in the data
            - Comparative analysis {"with similar districts" if compare_to_similar else "between district types"}
            - Potential future projections based on historical trends
            
            Format your response as JSON with the following structure:
            {{
                "trend_summary": "Overall assessment of the analyzed trends",
                "key_patterns": [
                    {{
                        "pattern_type": "trend|anomaly|volatility|comparison|projection",
                        "description": "Description of the identified pattern",
                        "affected_years": [year1, year2, ...],
                        "significance": "high|medium|low",
                        "potential_causes": ["Cause 1", "Cause 2", ...]
                    }},
                    // More patterns as applicable
                ],
                "year_over_year_analysis": [
                    {{
                        "years": "2022-2023", 
                        "percent_change": float,
                        "assessment": "Brief assessment of this yearly change"
                    }},
                    // More year pairs as applicable
                ],
                "long_term_assessment": "Assessment of the long-term trajectory",
                "rate_volatility": "Assessment of rate stability/volatility over time",
                "future_projection": "Projection of likely future trends",
                "district_type_insights": ["Insight 1", "Insight 2", ...], // If system-wide
                "comparative_insights": ["Insight 1", "Insight 2", ...], // If comparison requested
                "data_quality_assessment": "Assessment of data completeness and reliability",
                "next_analysis_recommendations": ["Recommendation 1", "Recommendation 2", ...]
            }}
            """
            
            # Use Claude to generate the analysis
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            try:
                result = json.loads(response)
                logger.info(f"Successfully generated levy trends analysis for {trend_type} data")
                
                # Sanitize the result to prevent XSS
                sanitized_result = sanitize_mcp_insights(result)
                
                # Combine raw data with analysis
                final_result = {
                    'trend_data': trend_data,
                    'analysis': sanitized_result
                }
                
                return final_result
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude response for trend analysis")
                fallback_response = {
                    "trend_data": trend_data,
                    "analysis": {
                        "trend_summary": "Error processing trend analysis",
                        "key_patterns": [],
                        "year_over_year_analysis": [],
                        "long_term_assessment": "Unable to assess long-term trajectory due to processing error",
                        "data_quality_assessment": "Analysis processing error, raw data available for manual review",
                        "next_analysis_recommendations": [
                            "Try analyzing a shorter time period",
                            "Verify data quality and completeness",
                            "Contact system administrator if the problem persists"
                        ]
                    }
                }
                return fallback_response
                
        except Exception as e:
            logger.error(f"Error in levy trend analysis: {str(e)}")
            return {
                "error": sanitize_html(str(e)),
                "trend_analysis": "Levy trend analysis failed to complete"
            }
    
    def audit_data_quality(self,
                          focus_areas: Optional[List[str]] = None,
                          district_id: Optional[str] = None,
                          comprehensive: bool = False) -> Dict[str, Any]:
        """
        Perform a comprehensive audit of data quality metrics for levy calculations.
        
        This capability assesses data quality across multiple dimensions including
        completeness, accuracy, consistency, and timeliness. It can focus on system-wide
        data quality or specific to a district.
        
        Args:
            focus_areas: List of specific areas to focus on ('completeness', 'accuracy', 
                        'consistency', 'timeliness') - if None, all areas are assessed
            district_id: Optional tax district ID to focus the audit on
            comprehensive: Whether to perform a deeper, more comprehensive audit
            
        Returns:
            Detailed data quality audit results with findings and recommendations
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "audit_results": "Data quality audit not available"
            }
        
        try:
            # Import required modules
            from flask import current_app
            from sqlalchemy import desc, func, case
            import logging
            from datetime import datetime, timedelta
            from models import DataQualityActivity
            
            # Get database session
            db = current_app.extensions.get('sqlalchemy').db
            
            # Import models (done here to avoid circular imports)
            from models import (
                TaxDistrict, TaxCode, Property, DataQualityScore, 
                ValidationRule, ValidationResult, ErrorPattern,
                ImportLog, LevyAuditRecord
            )
            
            # Default focus areas if none specified
            if not focus_areas:
                focus_areas = ['completeness', 'accuracy', 'consistency', 'timeliness']
            
            # Gather data quality metrics
            metrics = {}
            
            # Get latest data quality scores
            latest_score = db.session.query(DataQualityScore).order_by(
                desc(DataQualityScore.timestamp)
            ).first()
            
            if latest_score:
                metrics['overall_score'] = latest_score.overall_score
                metrics['completeness_score'] = latest_score.completeness_score
                metrics['accuracy_score'] = latest_score.accuracy_score
                metrics['consistency_score'] = latest_score.consistency_score
                metrics['timeliness_score'] = latest_score.timeliness_score
            
            # Get validation rule performance
            validation_rules = db.session.query(
                ValidationRule, 
                func.count(ValidationResult.id).label('total'),
                func.sum(ValidationResult.passed.cast(db.Integer)).label('passed')
            ).outerjoin(
                ValidationResult
            ).group_by(
                ValidationRule.id
            ).all()
            
            # Calculate metrics from validation results
            rule_metrics = []
            for rule, total, passed in validation_rules:
                if total > 0:
                    pass_rate = (passed / total) * 100
                else:
                    pass_rate = 0
                
                rule_metrics.append({
                    'id': rule.id,
                    'name': rule.name,
                    'category': rule.category,
                    'description': rule.description,
                    'pass_rate': pass_rate,
                    'passed': passed,
                    'failed': total - passed,
                    'total': total,
                    'severity': rule.severity
                })
            
            # Get error patterns
            error_patterns = db.session.query(ErrorPattern).filter(
                ErrorPattern.status == 'ACTIVE'
            ).order_by(desc(ErrorPattern.frequency)).limit(15).all()
            
            pattern_data = [{
                'name': pattern.name,
                'description': pattern.description,
                'category': pattern.category,
                'frequency': pattern.frequency,
                'impact': pattern.impact,
                'status': pattern.status
            } for pattern in error_patterns]
            
            # Get data counts for context
            property_count = db.session.query(func.count(Property.id)).scalar() or 0
            district_count = db.session.query(func.count(TaxDistrict.id)).scalar() or 0
            code_count = db.session.query(func.count(TaxCode.id)).scalar() or 0
            
            # Get recent import statistics (last 30 days)
            thirty_days_ago = datetime.now() - timedelta(days=30)
            import_stats = db.session.query(
                ImportLog.import_type,
                func.count(ImportLog.id).label('count'),
                func.avg(ImportLog.processed_records).label('avg_records'),
                func.sum(case([(ImportLog.success == True, 1)], else_=0)).label('success_count'),
                func.sum(case([(ImportLog.success == False, 1)], else_=0)).label('failure_count')
            ).filter(
                ImportLog.created_at >= thirty_days_ago
            ).group_by(
                ImportLog.import_type
            ).all()
            
            import_data = [{
                'type': import_type,
                'count': count,
                'avg_records': float(avg_records) if avg_records else 0,
                'success_rate': (success_count / count * 100) if count > 0 else 0,
                'failure_count': failure_count
            } for import_type, count, avg_records, success_count, failure_count in import_stats]
            
            # Compile all metrics
            all_metrics = {
                'timestamp': datetime.now().isoformat(),
                'data_counts': {
                    'properties': property_count,
                    'tax_districts': district_count,
                    'tax_codes': code_count
                },
                'quality_scores': {
                    'overall': latest_score.overall_score if latest_score else None,
                    'completeness': latest_score.completeness_score if latest_score else None,
                    'accuracy': latest_score.accuracy_score if latest_score else None,
                    'consistency': latest_score.consistency_score if latest_score else None,
                    'timeliness': latest_score.timeliness_score if latest_score else None
                },
                'validation_rules': rule_metrics,
                'error_patterns': pattern_data,
                'import_statistics': import_data,
                'focus_areas': focus_areas,
                'district_id': district_id,
                'comprehensive': comprehensive
            }
            
            # If specific district requested, add district-specific data
            if district_id:
                district_info = db.session.query(TaxDistrict).filter(
                    TaxDistrict.id == district_id
                ).first()
                
                if district_info:
                    # Get district-specific error patterns
                    district_errors = db.session.query(ErrorPattern).filter(
                        ErrorPattern.status == 'ACTIVE',
                        ErrorPattern.entity_type == 'tax_district',
                        ErrorPattern.entity_id == district_id
                    ).order_by(desc(ErrorPattern.frequency)).all()
                    
                    district_error_data = [{
                        'name': pattern.name,
                        'description': pattern.description,
                        'category': pattern.category,
                        'frequency': pattern.frequency,
                        'impact': pattern.impact
                    } for pattern in district_errors]
                    
                    # Get district levy audit history
                    audit_history = db.session.query(LevyAuditRecord).filter(
                        LevyAuditRecord.tax_district_id == district_id
                    ).order_by(desc(LevyAuditRecord.created_at)).limit(5).all()
                    
                    audit_data = [{
                        'id': audit.id,
                        'audit_type': audit.audit_type,
                        'year': audit.year,
                        'compliance_score': audit.compliance_score,
                        'status': audit.status,
                        'created_at': audit.created_at.isoformat() if audit.created_at else None
                    } for audit in audit_history]
                    
                    # Add to metrics
                    all_metrics['district'] = {
                        'name': district_info.name,
                        'type': district_info.district_type,
                        'error_patterns': district_error_data,
                        'audit_history': audit_data
                    }
            
            # Set up prompt for Claude analysis
            prompt = f"""
            As Lev, the world's foremost expert in property tax data quality and levy auditing, review the
            following data quality metrics and provide detailed analysis and recommendations.
            
            DATA QUALITY METRICS:
            {json.dumps(all_metrics, indent=2)}
            
            Perform a {"comprehensive" if comprehensive else "standard"} data quality audit focusing on:
            {', '.join(focus_areas)}
            
            Analyze the metrics to identify:
            1. Critical data quality issues that could impact levy calculations
            2. Patterns and trends in data quality problems
            3. Systemic issues versus isolated errors
            4. Potential root causes for recurring issues
            5. Compliance and regulatory concerns related to data quality
            
            For each focus area, provide:
            - A detailed assessment of current status
            - Key risks and issues identified
            - Specific recommendations for improvement
            - Priority levels for each recommendation
            
            Format your response as JSON with the following structure:
            {{
                "audit_summary": "Overall assessment of data quality",
                "overall_data_quality_score": float,  // 0-100 score based on your expert assessment
                "findings": [
                    {{
                        "focus_area": "One of: completeness, accuracy, consistency, timeliness",
                        "assessment": "Your assessment of this area",
                        "current_score": float,
                        "key_issues": ["Issue 1", "Issue 2", ...],
                        "risk_level": "critical|high|medium|low",
                        "potential_impact": "Description of potential impact on levy calculations"
                    }},
                    // More findings...
                ],
                "recommendations": [
                    {{
                        "title": "Clear title of recommendation",
                        "description": "Detailed explanation",
                        "focus_area": "The area this addresses",
                        "priority": "critical|high|medium|low",
                        "effort_level": "high|medium|low",
                        "estimated_impact": "high|medium|low"
                    }},
                    // More recommendations...
                ],
                "compliance_implications": [
                    "Implication 1",
                    "Implication 2",
                    // More implications...
                ],
                "data_quality_trends": "Assessment of trends in data quality over time",
                "next_steps": [
                    "Step 1",
                    "Step 2",
                    // More steps...
                ]
            }}
            """
            
            # Use Claude to generate the analysis
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            try:
                result = json.loads(response)
                logger.info("Successfully generated data quality audit")
                
                # Sanitize the result to prevent XSS
                sanitized_result = sanitize_mcp_insights(result)
                
                # Log the audit activity
                try:
                    activity = DataQualityActivity(
                        activity_type='AUDIT',
                        title='Data Quality Audit Completed',
                        description=f'Generated {"comprehensive" if comprehensive else "standard"} data quality audit focusing on {", ".join(focus_areas)}',
                        user_id=current_app.config.get('TESTING_USER_ID', 1),
                        entity_type='DataQualityAudit',
                        icon='shield-check',
                        icon_class='primary'
                    )
                    db.session.add(activity)
                    db.session.commit()
                except Exception as log_error:
                    logger.error(f"Error logging audit activity: {str(log_error)}")
                
                return sanitized_result
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude response for data quality audit")
                fallback_response = {
                    "audit_summary": "Error processing data quality audit",
                    "overall_data_quality_score": 0,
                    "findings": [],
                    "recommendations": [],
                    "compliance_implications": [
                        "Unable to assess compliance implications due to processing error"
                    ],
                    "data_quality_trends": "Error analyzing trends",
                    "next_steps": [
                        "Try running the audit again with more specific parameters",
                        "Contact system administrator if the problem persists"
                    ]
                }
                return fallback_response
                
        except Exception as e:
            logger.error(f"Error in data quality audit: {str(e)}")
            return {
                "error": sanitize_html(str(e)),
                "audit_results": "Data quality audit failed to complete"
            }

    def simulate_budget_impact(self,
                             district_id: Optional[str] = None,
                             scenario_parameters: Optional[Dict[str, Any]] = None,
                             year: Optional[int] = None,
                             multi_year: bool = False,
                             sensitivity_analysis: bool = False) -> Dict[str, Any]:
        """
        Simulate the budget impact of levy rate changes with AI-powered analysis.
        
        This capability extends standard budget simulations with AI-driven insights,
        impact analysis, and recommendations. It provides contextual understanding of
        how tax changes affect different stakeholders.
        
        Args:
            district_id: Optional tax district ID to focus analysis on
            scenario_parameters: Dictionary with simulation parameters
            year: Base year for simulation (defaults to current)
            multi_year: Whether to perform multi-year projections
            sensitivity_analysis: Whether to perform sensitivity analysis
            
        Returns:
            Detailed simulation results with AI-generated insights and visualizable data
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "simulation_results": "Budget impact simulation not available"
            }
        
        try:
            # Import required modules
            from flask import current_app
            from sqlalchemy import desc, func, case
            import logging
            from datetime import datetime, timedelta
            import numpy as np
            import json
            from models import (
                TaxDistrict, TaxCode, Property, TaxCodeHistoricalRate,
                ImportLog, LevyAuditRecord
            )
            
            # Get database session
            db = current_app.extensions.get('sqlalchemy').db
            
            # Set default year if not provided
            current_year = datetime.now().year
            if not year:
                year = current_year
                
            # Default scenario parameters if none provided
            if not scenario_parameters:
                scenario_parameters = {
                    'rate_change_percent': 0,
                    'assessed_value_change_percent': 0,
                    'inflation_rate': 2.0,
                    'population_growth_rate': 1.0,
                    'economic_growth_factor': 1.5,
                    'district_type_filters': [],
                    'revenue_targets': {},
                    'fixed_costs': {},
                    'variable_costs': {}
                }
                
            # Determine projection years for multi-year simulations
            projection_years = [year]
            if multi_year:
                projection_years = list(range(year, year + 5))  # 5-year projection
            
            # Get district data
            district_data = None
            if district_id:
                district = db.session.query(TaxDistrict).filter(
                    TaxDistrict.id == district_id,
                    TaxDistrict.year == year
                ).options(
                    db.joinedload(TaxDistrict.tax_codes)
                ).first()
                
                if not district:
                    return {
                        "error": f"Tax district with ID {district_id} not found for year {year}",
                        "simulation_results": {}
                    }
                
                # Get district baseline data
                district_data = {
                    'id': district.id,
                    'name': district.name,
                    'district_type': district.district_type,
                    'tax_codes': [{
                        'id': tc.id,
                        'code': tc.code,
                        'levy_rate': tc.levy_rate,
                        'total_levy_amount': tc.total_levy_amount,
                        'total_assessed_value': tc.total_assessed_value
                    } for tc in district.tax_codes],
                    'year': district.year
                }
                
                # Calculate district totals
                total_levy_amount = sum(tc.total_levy_amount or 0 for tc in district.tax_codes)
                total_assessed_value = sum(tc.total_assessed_value or 0 for tc in district.tax_codes)
                avg_levy_rate = 0
                if total_assessed_value > 0:
                    avg_levy_rate = (total_levy_amount / total_assessed_value) * 1000
                
                # Add district budget metrics
                district_data.update({
                    'total_levy_amount': total_levy_amount,
                    'total_assessed_value': total_assessed_value,
                    'avg_levy_rate': avg_levy_rate
                })
                
                # Get property count
                property_count = db.session.query(func.count(Property.id)).filter(
                    Property.tax_code_id.in_([tc.id for tc in district.tax_codes]),
                    Property.year == year
                ).scalar() or 0
                
                # Calculate average tax per property
                avg_tax_per_property = 0
                if property_count > 0:
                    avg_tax_per_property = total_levy_amount / property_count
                
                district_data.update({
                    'property_count': property_count,
                    'avg_tax_per_property': avg_tax_per_property
                })
                
                # Get historical data
                historical_years = list(range(year - 5, year))
                historical_data = []
                
                for hist_year in historical_years:
                    # Look for historical rates
                    yearly_rates = db.session.query(TaxCodeHistoricalRate).filter(
                        TaxCodeHistoricalRate.tax_code_id.in_([tc.id for tc in district.tax_codes]),
                        TaxCodeHistoricalRate.year == hist_year
                    ).all()
                    
                    if yearly_rates:
                        year_total_levy = sum(rate.levy_amount or 0 for rate in yearly_rates)
                        year_total_value = sum(rate.total_assessed_value or 0 for rate in yearly_rates)
                        year_avg_rate = 0
                        if year_total_value > 0:
                            year_avg_rate = (year_total_levy / year_total_value) * 1000
                            
                        historical_data.append({
                            'year': hist_year,
                            'total_levy_amount': year_total_levy,
                            'total_assessed_value': year_total_value,
                            'avg_levy_rate': year_avg_rate
                        })
                        
                district_data['historical_data'] = historical_data
            
            # If no specific district, get system-wide data
            else:
                # Get aggregate data for all districts
                districts = db.session.query(TaxDistrict).filter(
                    TaxDistrict.year == year
                ).options(
                    db.joinedload(TaxDistrict.tax_codes)
                ).all()
                
                if not districts:
                    return {
                        "error": f"No tax districts found for year {year}",
                        "simulation_results": {}
                    }
                
                # Calculate system-wide metrics
                total_levy_amount = 0
                total_assessed_value = 0
                total_property_count = 0
                district_data = []
                
                for district in districts:
                    district_levy_amount = sum(tc.total_levy_amount or 0 for tc in district.tax_codes)
                    district_assessed_value = sum(tc.total_assessed_value or 0 for tc in district.tax_codes)
                    district_avg_levy_rate = 0
                    if district_assessed_value > 0:
                        district_avg_levy_rate = (district_levy_amount / district_assessed_value) * 1000
                    
                    # Get property count
                    district_property_count = db.session.query(func.count(Property.id)).filter(
                        Property.tax_code_id.in_([tc.id for tc in district.tax_codes]),
                        Property.year == year
                    ).scalar() or 0
                    
                    # Calculate average tax per property
                    district_avg_tax_per_property = 0
                    if district_property_count > 0:
                        district_avg_tax_per_property = district_levy_amount / district_property_count
                    
                    district_data.append({
                        'id': district.id,
                        'name': district.name,
                        'district_type': district.district_type,
                        'total_levy_amount': district_levy_amount,
                        'total_assessed_value': district_assessed_value,
                        'avg_levy_rate': district_avg_levy_rate,
                        'property_count': district_property_count,
                        'avg_tax_per_property': district_avg_tax_per_property,
                        'year': district.year
                    })
                    
                    # Update system totals
                    total_levy_amount += district_levy_amount
                    total_assessed_value += district_assessed_value
                    total_property_count += district_property_count
                
                # Calculate system-wide averages
                system_avg_levy_rate = 0
                if total_assessed_value > 0:
                    system_avg_levy_rate = (total_levy_amount / total_assessed_value) * 1000
                
                system_avg_tax_per_property = 0
                if total_property_count > 0:
                    system_avg_tax_per_property = total_levy_amount / total_property_count
                
                # Create system-wide summary
                system_data = {
                    'total_levy_amount': total_levy_amount,
                    'total_assessed_value': total_assessed_value,
                    'avg_levy_rate': system_avg_levy_rate,
                    'property_count': total_property_count,
                    'avg_tax_per_property': system_avg_tax_per_property,
                    'districts': district_data,
                    'year': year
                }
                
                # Get historical system-wide data
                historical_years = list(range(year - 5, year))
                historical_data = []
                
                for hist_year in historical_years:
                    # Get aggregate data for historical year
                    yearly_rates = db.session.query(TaxCodeHistoricalRate).filter(
                        TaxCodeHistoricalRate.year == hist_year
                    ).all()
                    
                    if yearly_rates:
                        year_total_levy = sum(rate.levy_amount or 0 for rate in yearly_rates)
                        year_total_value = sum(rate.total_assessed_value or 0 for rate in yearly_rates)
                        year_avg_rate = 0
                        if year_total_value > 0:
                            year_avg_rate = (year_total_levy / year_total_value) * 1000
                            
                        historical_data.append({
                            'year': hist_year,
                            'total_levy_amount': year_total_levy,
                            'total_assessed_value': year_total_value,
                            'avg_levy_rate': year_avg_rate
                        })
                        
                system_data['historical_data'] = historical_data
                district_data = system_data
                
            # Now run the budget impact simulation
            simulation_results = {}
            
            # Extract scenario parameters
            rate_change_percent = scenario_parameters.get('rate_change_percent', 0)
            assessed_value_change_percent = scenario_parameters.get('assessed_value_change_percent', 0)
            inflation_rate = scenario_parameters.get('inflation_rate', 2.0)
            population_growth_rate = scenario_parameters.get('population_growth_rate', 1.0)
            economic_growth_factor = scenario_parameters.get('economic_growth_factor', 1.5)
            district_type_filters = scenario_parameters.get('district_type_filters', [])
            revenue_targets = scenario_parameters.get('revenue_targets', {})
            fixed_costs = scenario_parameters.get('fixed_costs', {})
            variable_costs = scenario_parameters.get('variable_costs', {})
            
            # Run simulation for single district or system-wide
            if district_id:
                # Deep copy district data for simulation
                district_sim = district_data.copy()
                district_sim['tax_codes'] = [tc.copy() for tc in district_data['tax_codes']]
                
                # Single-year simulation
                if not multi_year:
                    # Apply changes to each tax code
                    for tc in district_sim['tax_codes']:
                        # Apply rate change
                        if rate_change_percent != 0:
                            tc['levy_rate'] = tc['levy_rate'] * (1 + rate_change_percent / 100)
                        
                        # Apply assessed value change
                        if assessed_value_change_percent != 0:
                            tc['total_assessed_value'] = tc['total_assessed_value'] * (1 + assessed_value_change_percent / 100)
                        
                        # Recalculate levy amount
                        tc['total_levy_amount'] = (tc['levy_rate'] / 1000) * tc['total_assessed_value']
                    
                    # Recalculate district totals
                    district_sim['total_levy_amount'] = sum(tc['total_levy_amount'] for tc in district_sim['tax_codes'])
                    district_sim['total_assessed_value'] = sum(tc['total_assessed_value'] for tc in district_sim['tax_codes'])
                    
                    # Recalculate average levy rate
                    district_sim['avg_levy_rate'] = 0
                    if district_sim['total_assessed_value'] > 0:
                        district_sim['avg_levy_rate'] = (district_sim['total_levy_amount'] / district_sim['total_assessed_value']) * 1000
                    
                    # Recalculate average tax per property
                    district_sim['avg_tax_per_property'] = 0
                    if district_sim['property_count'] > 0:
                        district_sim['avg_tax_per_property'] = district_sim['total_levy_amount'] / district_sim['property_count']
                    
                    # Calculate impact metrics
                    impact = {
                        'levy_amount_change': district_sim['total_levy_amount'] - district_data['total_levy_amount'],
                        'levy_amount_percent': 0,
                        'assessed_value_change': district_sim['total_assessed_value'] - district_data['total_assessed_value'],
                        'assessed_value_percent': 0,
                        'levy_rate_change': district_sim['avg_levy_rate'] - district_data['avg_levy_rate'],
                        'levy_rate_percent': 0,
                        'tax_per_property_change': district_sim['avg_tax_per_property'] - district_data['avg_tax_per_property'],
                        'tax_per_property_percent': 0
                    }
                    
                    # Calculate percentages
                    if district_data['total_levy_amount'] > 0:
                        impact['levy_amount_percent'] = (impact['levy_amount_change'] / district_data['total_levy_amount']) * 100
                    
                    if district_data['total_assessed_value'] > 0:
                        impact['assessed_value_percent'] = (impact['assessed_value_change'] / district_data['total_assessed_value']) * 100
                    
                    if district_data['avg_levy_rate'] > 0:
                        impact['levy_rate_percent'] = (impact['levy_rate_change'] / district_data['avg_levy_rate']) * 100
                    
                    if district_data['avg_tax_per_property'] > 0:
                        impact['tax_per_property_percent'] = (impact['tax_per_property_change'] / district_data['avg_tax_per_property']) * 100
                    
                    district_sim['impact'] = impact
                    
                    # Add to simulation results
                    simulation_results = {
                        'baseline': district_data,
                        'simulation': district_sim,
                        'scenario': scenario_parameters,
                        'multi_year': False
                    }
                    
                # Multi-year simulation
                else:
                    multi_year_projections = []
                    cumulative_rate_change = 0
                    cumulative_value_change = 0
                    
                    # Project baseline as starting point
                    current_projection = district_data.copy()
                    current_projection['tax_codes'] = [tc.copy() for tc in district_data['tax_codes']]
                    
                    for proj_year in projection_years:
                        year_index = projection_years.index(proj_year)
                        
                        # Apply compounding changes only after first year
                        if year_index > 0:
                            # Calculate cumulative changes
                            cumulative_rate_change += rate_change_percent / 100
                            cumulative_value_change += assessed_value_change_percent / 100 + inflation_rate / 100
                            
                            # Apply to each tax code
                            for tc in current_projection['tax_codes']:
                                # Apply rate change
                                tc['levy_rate'] = district_data['tax_codes'][current_projection['tax_codes'].index(tc)]['levy_rate'] * (1 + cumulative_rate_change)
                                
                                # Apply assessed value change with inflation
                                tc['total_assessed_value'] = district_data['tax_codes'][current_projection['tax_codes'].index(tc)]['total_assessed_value'] * (1 + cumulative_value_change)
                                
                                # Recalculate levy amount
                                tc['total_levy_amount'] = (tc['levy_rate'] / 1000) * tc['total_assessed_value']
                            
                            # Adjust property count for population growth
                            current_projection['property_count'] = district_data['property_count'] * (1 + (population_growth_rate / 100) * year_index)
                        
                        # Recalculate district totals
                        current_projection['total_levy_amount'] = sum(tc['total_levy_amount'] for tc in current_projection['tax_codes'])
                        current_projection['total_assessed_value'] = sum(tc['total_assessed_value'] for tc in current_projection['tax_codes'])
                        
                        # Recalculate average levy rate
                        current_projection['avg_levy_rate'] = 0
                        if current_projection['total_assessed_value'] > 0:
                            current_projection['avg_levy_rate'] = (current_projection['total_levy_amount'] / current_projection['total_assessed_value']) * 1000
                        
                        # Recalculate average tax per property
                        current_projection['avg_tax_per_property'] = 0
                        if current_projection['property_count'] > 0:
                            current_projection['avg_tax_per_property'] = current_projection['total_levy_amount'] / current_projection['property_count']
                        
                        # Calculate impact compared to baseline
                        impact = {
                            'levy_amount_change': current_projection['total_levy_amount'] - district_data['total_levy_amount'],
                            'levy_amount_percent': 0,
                            'assessed_value_change': current_projection['total_assessed_value'] - district_data['total_assessed_value'],
                            'assessed_value_percent': 0,
                            'levy_rate_change': current_projection['avg_levy_rate'] - district_data['avg_levy_rate'],
                            'levy_rate_percent': 0,
                            'tax_per_property_change': current_projection['avg_tax_per_property'] - district_data['avg_tax_per_property'],
                            'tax_per_property_percent': 0
                        }
                        
                        # Calculate percentages
                        if district_data['total_levy_amount'] > 0:
                            impact['levy_amount_percent'] = (impact['levy_amount_change'] / district_data['total_levy_amount']) * 100
                        
                        if district_data['total_assessed_value'] > 0:
                            impact['assessed_value_percent'] = (impact['assessed_value_change'] / district_data['total_assessed_value']) * 100
                        
                        if district_data['avg_levy_rate'] > 0:
                            impact['levy_rate_percent'] = (impact['levy_rate_change'] / district_data['avg_levy_rate']) * 100
                        
                        if district_data['avg_tax_per_property'] > 0:
                            impact['tax_per_property_percent'] = (impact['tax_per_property_change'] / district_data['avg_tax_per_property']) * 100
                        
                        # Create year projection
                        year_projection = current_projection.copy()
                        year_projection['year'] = proj_year
                        year_projection['impact'] = impact
                        
                        multi_year_projections.append(year_projection)
                    
                    # Add to simulation results
                    simulation_results = {
                        'baseline': district_data,
                        'projections': multi_year_projections,
                        'scenario': scenario_parameters,
                        'multi_year': True
                    }
                    
                # Add sensitivity analysis if requested
                if sensitivity_analysis:
                    sensitivity_scenarios = []
                    
                    # Generate sensitivity test cases
                    test_rate_changes = [
                        rate_change_percent - 2,
                        rate_change_percent - 1, 
                        rate_change_percent, 
                        rate_change_percent + 1, 
                        rate_change_percent + 2
                    ]
                    
                    test_value_changes = [
                        assessed_value_change_percent - 2,
                        assessed_value_change_percent - 1,
                        assessed_value_change_percent,
                        assessed_value_change_percent + 1,
                        assessed_value_change_percent + 2
                    ]
                    
                    # Run simulation for each test case
                    for test_rate in test_rate_changes:
                        # Deep copy district data
                        test_sim = district_data.copy()
                        test_sim['tax_codes'] = [tc.copy() for tc in district_data['tax_codes']]
                        
                        # Apply test rate to each tax code
                        for tc in test_sim['tax_codes']:
                            tc['levy_rate'] = tc['levy_rate'] * (1 + test_rate / 100)
                            tc['total_levy_amount'] = (tc['levy_rate'] / 1000) * tc['total_assessed_value']
                        
                        # Recalculate totals
                        test_sim['total_levy_amount'] = sum(tc['total_levy_amount'] for tc in test_sim['tax_codes'])
                        test_sim['avg_levy_rate'] = 0
                        if test_sim['total_assessed_value'] > 0:
                            test_sim['avg_levy_rate'] = (test_sim['total_levy_amount'] / test_sim['total_assessed_value']) * 1000
                        
                        # Calculate impact
                        levy_amount_change = test_sim['total_levy_amount'] - district_data['total_levy_amount']
                        levy_amount_percent = 0
                        if district_data['total_levy_amount'] > 0:
                            levy_amount_percent = (levy_amount_change / district_data['total_levy_amount']) * 100
                            
                        # Add to sensitivity scenarios
                        sensitivity_scenarios.append({
                            'parameter': 'rate_change_percent',
                            'value': test_rate,
                            'result': {
                                'total_levy_amount': test_sim['total_levy_amount'],
                                'change': levy_amount_change,
                                'percent': levy_amount_percent
                            }
                        })
                    
                    for test_value in test_value_changes:
                        # Deep copy district data
                        test_sim = district_data.copy()
                        test_sim['tax_codes'] = [tc.copy() for tc in district_data['tax_codes']]
                        
                        # Apply test value to each tax code
                        for tc in test_sim['tax_codes']:
                            tc['total_assessed_value'] = tc['total_assessed_value'] * (1 + test_value / 100)
                            tc['total_levy_amount'] = (tc['levy_rate'] / 1000) * tc['total_assessed_value']
                        
                        # Recalculate totals
                        test_sim['total_levy_amount'] = sum(tc['total_levy_amount'] for tc in test_sim['tax_codes'])
                        test_sim['total_assessed_value'] = sum(tc['total_assessed_value'] for tc in test_sim['tax_codes'])
                        
                        # Calculate impact
                        levy_amount_change = test_sim['total_levy_amount'] - district_data['total_levy_amount']
                        levy_amount_percent = 0
                        if district_data['total_levy_amount'] > 0:
                            levy_amount_percent = (levy_amount_change / district_data['total_levy_amount']) * 100
                            
                        # Add to sensitivity scenarios
                        sensitivity_scenarios.append({
                            'parameter': 'assessed_value_change_percent',
                            'value': test_value,
                            'result': {
                                'total_levy_amount': test_sim['total_levy_amount'],
                                'change': levy_amount_change,
                                'percent': levy_amount_percent
                            }
                        })
                    
                    # Add sensitivity analysis to results
                    simulation_results['sensitivity_analysis'] = sensitivity_scenarios
            
            # System-wide simulation for multiple districts
            else:
                # Single-year simulation
                if not multi_year:
                    # Deep copy system data for simulation
                    system_sim = system_data.copy()
                    system_sim['districts'] = [d.copy() for d in system_data['districts']]
                    
                    # Apply changes to each district
                    for dist in system_sim['districts']:
                        # Apply filter - only modify districts of specified types if filters provided
                        if district_type_filters and dist['district_type'] not in district_type_filters:
                            continue
                        
                        # Apply rate change
                        if rate_change_percent != 0:
                            dist['avg_levy_rate'] = dist['avg_levy_rate'] * (1 + rate_change_percent / 100)
                        
                        # Apply assessed value change
                        if assessed_value_change_percent != 0:
                            dist['total_assessed_value'] = dist['total_assessed_value'] * (1 + assessed_value_change_percent / 100)
                        
                        # Recalculate levy amount
                        dist['total_levy_amount'] = (dist['avg_levy_rate'] / 1000) * dist['total_assessed_value']
                        
                        # Recalculate average tax per property
                        if dist['property_count'] > 0:
                            dist['avg_tax_per_property'] = dist['total_levy_amount'] / dist['property_count']
                    
                    # Recalculate system totals
                    system_sim['total_levy_amount'] = sum(d['total_levy_amount'] for d in system_sim['districts'])
                    system_sim['total_assessed_value'] = sum(d['total_assessed_value'] for d in system_sim['districts'])
                    
                    # Recalculate average levy rate
                    system_sim['avg_levy_rate'] = 0
                    if system_sim['total_assessed_value'] > 0:
                        system_sim['avg_levy_rate'] = (system_sim['total_levy_amount'] / system_sim['total_assessed_value']) * 1000
                    
                    # Recalculate average tax per property
                    system_sim['avg_tax_per_property'] = 0
                    if system_sim['property_count'] > 0:
                        system_sim['avg_tax_per_property'] = system_sim['total_levy_amount'] / system_sim['property_count']
                    
                    # Calculate impact metrics
                    impact = {
                        'levy_amount_change': system_sim['total_levy_amount'] - system_data['total_levy_amount'],
                        'levy_amount_percent': 0,
                        'assessed_value_change': system_sim['total_assessed_value'] - system_data['total_assessed_value'],
                        'assessed_value_percent': 0,
                        'levy_rate_change': system_sim['avg_levy_rate'] - system_data['avg_levy_rate'],
                        'levy_rate_percent': 0,
                        'tax_per_property_change': system_sim['avg_tax_per_property'] - system_data['avg_tax_per_property'],
                        'tax_per_property_percent': 0
                    }
                    
                    # Calculate percentages
                    if system_data['total_levy_amount'] > 0:
                        impact['levy_amount_percent'] = (impact['levy_amount_change'] / system_data['total_levy_amount']) * 100
                    
                    if system_data['total_assessed_value'] > 0:
                        impact['assessed_value_percent'] = (impact['assessed_value_change'] / system_data['total_assessed_value']) * 100
                    
                    if system_data['avg_levy_rate'] > 0:
                        impact['levy_rate_percent'] = (impact['levy_rate_change'] / system_data['avg_levy_rate']) * 100
                    
                    if system_data['avg_tax_per_property'] > 0:
                        impact['tax_per_property_percent'] = (impact['tax_per_property_change'] / system_data['avg_tax_per_property']) * 100
                    
                    system_sim['impact'] = impact
                    
                    # District-level impacts
                    district_impacts = {}
                    for sim_dist in system_sim['districts']:
                        dist_id = sim_dist['id']
                        base_dist = next((d for d in system_data['districts'] if d['id'] == dist_id), None)
                        
                        if base_dist:
                            dist_impact = {
                                'levy_amount_change': sim_dist['total_levy_amount'] - base_dist['total_levy_amount'],
                                'levy_amount_percent': 0,
                                'assessed_value_change': sim_dist['total_assessed_value'] - base_dist['total_assessed_value'],
                                'assessed_value_percent': 0,
                                'levy_rate_change': sim_dist['avg_levy_rate'] - base_dist['avg_levy_rate'],
                                'levy_rate_percent': 0,
                                'tax_per_property_change': sim_dist['avg_tax_per_property'] - base_dist['avg_tax_per_property'],
                                'tax_per_property_percent': 0
                            }
                            
                            # Calculate percentages
                            if base_dist['total_levy_amount'] > 0:
                                dist_impact['levy_amount_percent'] = (dist_impact['levy_amount_change'] / base_dist['total_levy_amount']) * 100
                            
                            if base_dist['total_assessed_value'] > 0:
                                dist_impact['assessed_value_percent'] = (dist_impact['assessed_value_change'] / base_dist['total_assessed_value']) * 100
                            
                            if base_dist['avg_levy_rate'] > 0:
                                dist_impact['levy_rate_percent'] = (dist_impact['levy_rate_change'] / base_dist['avg_levy_rate']) * 100
                            
                            if base_dist['avg_tax_per_property'] > 0:
                                dist_impact['tax_per_property_percent'] = (dist_impact['tax_per_property_change'] / base_dist['avg_tax_per_property']) * 100
                            
                            district_impacts[dist_id] = dist_impact
                    
                    system_sim['district_impacts'] = district_impacts
                    
                    # Add to simulation results
                    simulation_results = {
                        'baseline': system_data,
                        'simulation': system_sim,
                        'scenario': scenario_parameters,
                        'multi_year': False
                    }
                    
                # Multi-year simulation
                else:
                    multi_year_projections = []
                    cumulative_rate_change = 0
                    cumulative_value_change = 0
                    
                    # Project baseline as starting point
                    current_projection = system_data.copy()
                    current_projection['districts'] = [d.copy() for d in system_data['districts']]
                    
                    for proj_year in projection_years:
                        year_index = projection_years.index(proj_year)
                        
                        # Apply compounding changes only after first year
                        if year_index > 0:
                            # Calculate cumulative changes
                            cumulative_rate_change += rate_change_percent / 100
                            cumulative_value_change += assessed_value_change_percent / 100 + inflation_rate / 100
                            
                            # Apply to each district
                            for dist in current_projection['districts']:
                                # Skip districts not in filter if specified
                                if district_type_filters and dist['district_type'] not in district_type_filters:
                                    continue
                                
                                # Apply rate change
                                base_dist = next((d for d in system_data['districts'] if d['id'] == dist['id']), None)
                                if base_dist:
                                    dist['avg_levy_rate'] = base_dist['avg_levy_rate'] * (1 + cumulative_rate_change)
                                    
                                    # Apply assessed value change with inflation
                                    dist['total_assessed_value'] = base_dist['total_assessed_value'] * (1 + cumulative_value_change)
                                    
                                    # Recalculate levy amount
                                    dist['total_levy_amount'] = (dist['avg_levy_rate'] / 1000) * dist['total_assessed_value']
                                    
                                    # Adjust property count for population growth
                                    dist['property_count'] = base_dist['property_count'] * (1 + (population_growth_rate / 100) * year_index)
                                    
                                    # Recalculate average tax per property
                                    if dist['property_count'] > 0:
                                        dist['avg_tax_per_property'] = dist['total_levy_amount'] / dist['property_count']
                        
                        # Recalculate system totals
                        current_projection['total_levy_amount'] = sum(d['total_levy_amount'] for d in current_projection['districts'])
                        current_projection['total_assessed_value'] = sum(d['total_assessed_value'] for d in current_projection['districts'])
                        current_projection['property_count'] = sum(d['property_count'] for d in current_projection['districts'])
                        
                        # Recalculate average levy rate
                        current_projection['avg_levy_rate'] = 0
                        if current_projection['total_assessed_value'] > 0:
                            current_projection['avg_levy_rate'] = (current_projection['total_levy_amount'] / current_projection['total_assessed_value']) * 1000
                        
                        # Recalculate average tax per property
                        current_projection['avg_tax_per_property'] = 0
                        if current_projection['property_count'] > 0:
                            current_projection['avg_tax_per_property'] = current_projection['total_levy_amount'] / current_projection['property_count']
                        
                        # Calculate impact compared to baseline
                        impact = {
                            'levy_amount_change': current_projection['total_levy_amount'] - system_data['total_levy_amount'],
                            'levy_amount_percent': 0,
                            'assessed_value_change': current_projection['total_assessed_value'] - system_data['total_assessed_value'],
                            'assessed_value_percent': 0,
                            'levy_rate_change': current_projection['avg_levy_rate'] - system_data['avg_levy_rate'],
                            'levy_rate_percent': 0,
                            'tax_per_property_change': current_projection['avg_tax_per_property'] - system_data['avg_tax_per_property'],
                            'tax_per_property_percent': 0
                        }
                        
                        # Calculate percentages
                        if system_data['total_levy_amount'] > 0:
                            impact['levy_amount_percent'] = (impact['levy_amount_change'] / system_data['total_levy_amount']) * 100
                        
                        if system_data['total_assessed_value'] > 0:
                            impact['assessed_value_percent'] = (impact['assessed_value_change'] / system_data['total_assessed_value']) * 100
                        
                        if system_data['avg_levy_rate'] > 0:
                            impact['levy_rate_percent'] = (impact['levy_rate_change'] / system_data['avg_levy_rate']) * 100
                        
                        if system_data['avg_tax_per_property'] > 0:
                            impact['tax_per_property_percent'] = (impact['tax_per_property_change'] / system_data['avg_tax_per_property']) * 100
                        
                        # Create year projection
                        year_projection = current_projection.copy()
                        year_projection['year'] = proj_year
                        year_projection['impact'] = impact
                        
                        # Calculate district impacts
                        district_impacts = {}
                        for proj_dist in year_projection['districts']:
                            dist_id = proj_dist['id']
                            base_dist = next((d for d in system_data['districts'] if d['id'] == dist_id), None)
                            
                            if base_dist:
                                dist_impact = {
                                    'levy_amount_change': proj_dist['total_levy_amount'] - base_dist['total_levy_amount'],
                                    'levy_amount_percent': 0,
                                    'assessed_value_change': proj_dist['total_assessed_value'] - base_dist['total_assessed_value'],
                                    'assessed_value_percent': 0,
                                    'levy_rate_change': proj_dist['avg_levy_rate'] - base_dist['avg_levy_rate'],
                                    'levy_rate_percent': 0,
                                    'tax_per_property_change': proj_dist['avg_tax_per_property'] - base_dist['avg_tax_per_property'],
                                    'tax_per_property_percent': 0
                                }
                                
                                # Calculate percentages
                                if base_dist['total_levy_amount'] > 0:
                                    dist_impact['levy_amount_percent'] = (dist_impact['levy_amount_change'] / base_dist['total_levy_amount']) * 100
                                
                                if base_dist['total_assessed_value'] > 0:
                                    dist_impact['assessed_value_percent'] = (dist_impact['assessed_value_change'] / base_dist['total_assessed_value']) * 100
                                
                                if base_dist['avg_levy_rate'] > 0:
                                    dist_impact['levy_rate_percent'] = (dist_impact['levy_rate_change'] / base_dist['avg_levy_rate']) * 100
                                
                                if base_dist['avg_tax_per_property'] > 0:
                                    dist_impact['tax_per_property_percent'] = (dist_impact['tax_per_property_change'] / base_dist['avg_tax_per_property']) * 100
                                
                                district_impacts[dist_id] = dist_impact
                        
                        year_projection['district_impacts'] = district_impacts
                        
                        multi_year_projections.append(year_projection)
                    
                    # Add to simulation results
                    simulation_results = {
                        'baseline': system_data,
                        'projections': multi_year_projections,
                        'scenario': scenario_parameters,
                        'multi_year': True
                    }
            
            # Now use Claude to generate insights about the simulation
            prompt = f"""
            As Lev, the world's foremost expert in property tax and levy analysis, review the
            following budget impact simulation results and provide detailed insights and recommendations.
            
            SIMULATION RESULTS:
            {json.dumps(simulation_results, indent=2)}
            
            Your analysis should cover:
            1. Overall assessment of the budget impact scenario
            2. Key insights about revenue changes and tax burdens
            3. Potential stakeholder impacts (taxpayers, district services, etc.)
            4. Recommendations for optimizing the scenario
            5. Risks and considerations for implementation
            6. Comparative analysis to historical trends
            7. {"Analysis of multi-year projections and long-term sustainability" if multi_year else ""}
            8. {"Sensitivity analysis insights and risk factors" if sensitivity_analysis else ""}
            
            Format your response as JSON with the following structure:
            {{
                "executive_summary": "Clear, concise summary of the simulation results and key takeaways",
                "key_insights": [
                    {{
                        "area": "revenue|equity|taxpayer_impact|sustainability|other",
                        "insight": "Detailed insight description",
                        "significance": "high|medium|low"
                    }},
                    // Additional insights
                ],
                "stakeholder_impacts": [
                    {{
                        "stakeholder": "taxpayers|district_services|businesses|residential",
                        "impact": "Description of specific impact on this stakeholder group",
                        "magnitude": "positive|negative|mixed|neutral",
                        "scale": "high|medium|low"
                    }},
                    // Additional stakeholder impacts
                ],
                "recommendations": [
                    {{
                        "title": "Concise recommendation title",
                        "description": "Detailed explanation of the recommendation",
                        "priority": "high|medium|low"
                    }},
                    // Additional recommendations
                ],
                "implementation_considerations": [
                    "Consideration 1",
                    "Consideration 2",
                    // Additional considerations
                ],
                "historical_context": "Analysis comparing simulation to historical trends",
                "multi_year_assessment": "Assessment of long-term projections and sustainability",
                "optimal_scenario": {{
                    "rate_change": recommended rate change value,
                    "value_change": recommended value change value,
                    "justification": "Explanation of why this scenario is optimal"
                }},
                "optimization_recommendations": {{
                    "property_value_growth": optimized property value growth percentage as float,
                    "new_construction_growth": optimized new construction growth percentage as float,
                    "exemption_rate": optimized exemption rate percentage as float,
                    "tax_rate_adjustment": optimized tax rate adjustment percentage as float,
                    "compliance_rate": optimized compliance rate percentage as float,
                    "collection_efficiency": optimized collection efficiency percentage as float,
                    "explanation": "Detailed explanation of how these optimized parameters improve budget outcomes"
                }}
            }}
            """
            
            # Use Claude to generate the analysis
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            try:
                ai_insights = json.loads(response)
                logger.info("Successfully generated budget impact simulation insights")
                
                # Sanitize the result to prevent XSS
                sanitized_insights = sanitize_mcp_insights(ai_insights)
                
                # Add AI insights to simulation results
                simulation_results['ai_insights'] = sanitized_insights
                
                return simulation_results
                
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON from Claude response for budget impact simulation")
                fallback_insights = {
                    "executive_summary": "Unable to generate AI insights for this budget impact simulation due to processing error.",
                    "key_insights": [],
                    "stakeholder_impacts": [],
                    "recommendations": [
                        {
                            "title": "Review simulation parameters",
                            "description": "The current scenario parameters may need adjustment to ensure realistic projections.",
                            "priority": "medium"
                        }
                    ],
                    "implementation_considerations": [
                        "Simulation completed successfully, but AI analysis encountered an error.",
                        "Raw numerical results are available for manual review."
                    ],
                    "optimization_recommendations": {
                        "property_value_growth": 2.0,
                        "new_construction_growth": 1.5,
                        "exemption_rate": 0.5,
                        "tax_rate_adjustment": 1.0,
                        "compliance_rate": 98.0,
                        "collection_efficiency": 97.0,
                        "explanation": "These are default recommended values. Please rerun the AI simulation for customized recommendations."
                    }
                }
                
                # Add fallback insights to simulation results
                simulation_results['ai_insights'] = fallback_insights
                
                return simulation_results
                
        except Exception as e:
            logger.error(f"Error in budget impact simulation: {str(e)}")
            return {
                "error": sanitize_html(str(e)),
                "simulation_results": "Budget impact simulation failed to complete"
            }
    
    def verify_levy_calculation(self,
                              tax_code_id: str,
                              property_value: float,
                              year: Optional[int] = None) -> Dict[str, Any]:
        """
        Verify a levy calculation and provide expert analysis.
        
        Args:
            tax_code_id: Tax code identifier
            property_value: Property assessed value
            year: Assessment year (optional, defaults to current)
            
        Returns:
            Verification results with detailed analysis and recommendations
        """
        if not self.claude:
            return {
                "error": "Claude service not available",
                "verification": "Levy calculation verification not available"
            }
        
        try:
            # Get tax code details
            tax_code = registry.execute_function(
                "get_tax_code_details",
                {"tax_code_id": tax_code_id}
            )
            
            # Get district information
            district_id = tax_code.get("tax_district_id")
            district = registry.execute_function(
                "get_district_details",
                {"district_id": district_id}
            )
            
            # Calculate levy amount
            levy_rate = tax_code.get("levy_rate", 0)
            
            # If year is provided, try to get the historical rate
            if year:
                historical_rate = registry.execute_function(
                    "get_historical_rate",
                    {"tax_code_id": tax_code_id, "year": year}
                )
                if historical_rate:
                    levy_rate = historical_rate.get("levy_rate", levy_rate)
            
            # Calculate tax amount (property value / 1000 * levy rate)
            calculated_amount = (property_value / 1000) * levy_rate
            
            # Prepare data for verification
            verification_data = {
                "tax_code": tax_code,
                "district": district,
                "property_value": property_value,
                "levy_rate": levy_rate,
                "calculated_amount": calculated_amount,
                "year": year or "current"
            }
            
            prompt = f"""
            As Lev, the world's foremost expert in property tax and levy calculation, verify and analyze the following levy calculation:
            
            Tax Code Information:
            {json.dumps(tax_code, indent=2)}
            
            District Information:
            {json.dumps(district, indent=2)}
            
            Calculation Details:
            - Property Value: ${property_value:,.2f}
            - Levy Rate: {levy_rate} per $1,000 assessed value
            - Calculated Levy Amount: ${calculated_amount:,.2f}
            - Assessment Year: {year or "Current"}
            
            Please provide:
            1. Verification of this calculation's accuracy
            2. Analysis of the effective tax rate relative to comparable properties/districts
            3. Applicable exemptions or special considerations that might apply
            4. Recommendations for the property owner or tax authority
            
            Format your response as JSON with the following structure:
            {{
                "verification_result": "correct|incorrect|needs_review",
                "calculation_analysis": "string",
                "effective_tax_rate": "percentage as float",
                "comparative_analysis": "string",
                "potential_exemptions": ["string", "string", ...],
                "recommendations": ["string", "string", ...],
                "additional_insights": "string"
            }}
            """
            
            # Use Claude to verify the calculation
            response = self.claude.generate_text(prompt)
            
            # Extract JSON from response
            result = json.loads(response)
            logger.info(f"Successfully verified levy calculation for tax code {tax_code_id}")
            
            # Add the calculation details to the result
            result["calculation_details"] = {
                "property_value": property_value,
                "levy_rate": levy_rate,
                "calculated_amount": calculated_amount,
                "tax_code": tax_code.get("tax_code", tax_code_id),
                "district_name": district.get("name", "Unknown District"),
                "year": year or "current"
            }
            
            # Sanitize the result to prevent XSS
            sanitized_result = sanitize_mcp_insights(result)
            return sanitized_result
            
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from Claude response")
            return {
                "verification_result": "error",
                "calculation_analysis": "Error processing verification request",
                "effective_tax_rate": 0.0,
                "comparative_analysis": "",
                "potential_exemptions": [],
                "recommendations": [
                    "Please try the verification again",
                    "Contact system administrator if the problem persists"
                ],
                "additional_insights": "",
                "calculation_details": {
                    "property_value": property_value,
                    "levy_rate": 0,
                    "calculated_amount": 0,
                    "tax_code": tax_code_id,
                    "district_name": "Unknown",
                    "year": year or "current"
                }
            }
        except Exception as e:
            logger.error(f"Error verifying levy calculation: {str(e)}")
            return {"error": sanitize_html(str(e))}


# Singleton instance
levy_audit_agent = None

def init_levy_audit_agent():
    """Initialize the levy audit agent and register its functions."""
    global levy_audit_agent
    
    try:
        # Create the agent instance
        agent = LevyAuditAgent()
        
        # Register the agent's functions with the MCP registry
        registry.register_function(
            func=agent.audit_levy_compliance,
            name="audit_levy_compliance",
            description="Audit a tax district's levy for compliance with applicable laws",
            parameter_schema={
                "type": "object",
                "properties": {
                    "district_id": {
                        "type": "string",
                        "description": "Tax district identifier"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Assessment year"
                    },
                    "full_audit": {
                        "type": "boolean",
                        "description": "Whether to perform a comprehensive audit"
                    }
                },
                "required": ["district_id", "year"]
            }
        )
        
        registry.register_function(
            func=agent.explain_levy_law,
            name="explain_levy_law",
            description="Provide expert explanation of property tax and levy laws",
            parameter_schema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The specific levy or tax law topic to explain"
                    },
                    "jurisdiction": {
                        "type": "string",
                        "description": "State or jurisdiction code"
                    },
                    "level_of_detail": {
                        "type": "string",
                        "description": "Level of detail for the explanation (basic, standard, detailed)"
                    }
                },
                "required": ["topic"]
            }
        )
        
        registry.register_function(
            func=agent.provide_levy_recommendations,
            name="provide_levy_recommendations",
            description="Generate contextual recommendations for levy optimization and compliance",
            parameter_schema={
                "type": "object",
                "properties": {
                    "district_id": {
                        "type": "string",
                        "description": "Tax district identifier"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Assessment year"
                    },
                    "focus_area": {
                        "type": "string",
                        "description": "Specific area of focus (compliance, optimization, public communication)"
                    }
                },
                "required": ["district_id", "year"]
            }
        )
        
        registry.register_function(
            func=agent.process_levy_query,
            name="process_levy_query",
            description="Process a natural language query about levy and property tax topics",
            parameter_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "context": {
                        "type": "object",
                        "description": "Additional context for the query (district, year, etc.)"
                    },
                    "add_to_history": {
                        "type": "boolean",
                        "description": "Whether to add this interaction to conversation history"
                    }
                },
                "required": ["query"]
            }
        )
        
        registry.register_function(
            func=agent.verify_levy_calculation,
            name="verify_levy_calculation",
            description="Verify a levy calculation and provide expert analysis",
            parameter_schema={
                "type": "object",
                "properties": {
                    "tax_code_id": {
                        "type": "string",
                        "description": "Tax code identifier"
                    },
                    "property_value": {
                        "type": "number",
                        "description": "Property assessed value"
                    },
                    "year": {
                        "type": "integer",
                        "description": "Assessment year (optional, defaults to current)"
                    }
                },
                "required": ["tax_code_id", "property_value"]
            }
        )
        
        registry.register_function(
            func=agent.analyze_levy_trends,
            name="analyze_levy_trends",
            description="Analyze historical trends in levy rates and property taxes",
            parameter_schema={
                "type": "object",
                "properties": {
                    "district_id": {
                        "type": "string",
                        "description": "Tax district ID to focus analysis on (optional)"
                    },
                    "tax_code_id": {
                        "type": "string",
                        "description": "Tax code ID to focus analysis on (optional)"
                    },
                    "year_range": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "description": "List containing start and end years for analysis, e.g. [2018, 2025]"
                    },
                    "trend_type": {
                        "type": "string",
                        "description": "Type of trend analysis - 'rate', 'value', 'revenue', or 'comprehensive'",
                        "enum": ["rate", "value", "revenue", "comprehensive"]
                    },
                    "compare_to_similar": {
                        "type": "boolean",
                        "description": "Whether to compare trends with similar districts/areas"
                    }
                }
            }
        )
        
        registry.register_function(
            func=agent.audit_data_quality,
            name="audit_data_quality",
            description="Perform a comprehensive audit of data quality metrics for levy calculations",
            parameter_schema={
                "type": "object",
                "properties": {
                    "focus_areas": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["completeness", "accuracy", "consistency", "timeliness"]
                        },
                        "description": "Specific areas to focus on ('completeness', 'accuracy', 'consistency', 'timeliness')"
                    },
                    "district_id": {
                        "type": "string",
                        "description": "Optional tax district ID to focus the audit on"
                    },
                    "comprehensive": {
                        "type": "boolean",
                        "description": "Whether to perform a deeper, more comprehensive audit"
                    }
                }
            }
        )
        
        registry.register_function(
            func=agent.simulate_budget_impact,
            name="simulate_budget_impact",
            description="Simulate the budget impact of levy rate changes with AI-powered analysis",
            parameter_schema={
                "type": "object",
                "properties": {
                    "district_id": {
                        "type": "string",
                        "description": "Optional tax district ID to focus analysis on"
                    },
                    "scenario_parameters": {
                        "type": "object",
                        "description": "Dictionary with simulation parameters including rate_change_percent, assessed_value_change_percent, etc."
                    },
                    "year": {
                        "type": "integer",
                        "description": "Base year for simulation (defaults to current)"
                    },
                    "multi_year": {
                        "type": "boolean",
                        "description": "Whether to perform multi-year projections"
                    },
                    "sensitivity_analysis": {
                        "type": "boolean",
                        "description": "Whether to perform sensitivity analysis"
                    }
                }
            }
        )
        
        logger.info("Levy Audit Agent initialized and registered")
        return agent
        
    except Exception as e:
        logger.error(f"Error initializing levy audit agent: {str(e)}")
        return None


def get_levy_audit_agent():
    """Get the levy audit agent instance, initializing it if necessary."""
    global levy_audit_agent
    if levy_audit_agent is None:
        try:
            levy_audit_agent = init_levy_audit_agent()
            if levy_audit_agent is None:
                logger.error("Failed to initialize levy audit agent")
                # Create a new instance if initialization failed
                levy_audit_agent = LevyAuditAgent()
        except Exception as e:
            logger.error(f"Error initializing levy audit agent: {str(e)}")
            # Create a new instance if initialization failed with an exception
            levy_audit_agent = LevyAuditAgent()
    return levy_audit_agent