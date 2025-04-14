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