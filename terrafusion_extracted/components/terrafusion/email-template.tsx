interface EmailTemplateProps {
  title: string
  content: string
  ctaText: string
  ctaUrl: string
}

export function EmailTemplate({ title, content, ctaText, ctaUrl }: EmailTemplateProps) {
  return (
    <div className="w-full max-w-[600px] mx-auto border border-gray-200 rounded-md overflow-hidden font-sans">
      {/* Header with Monoline Seal */}
      <div className="h-32 bg-gradient-to-r from-[#3DBE82] via-[#5A9BD5] to-[#C080FF] flex items-center justify-center">
        <div className="w-[72px] h-[72px] bg-white rounded-full flex items-center justify-center">
          <div className="w-[60px] h-[60px] rounded-full border-2 border-[#2E7D32] flex items-center justify-center text-[#2E7D32] font-bold text-xl">
            TF
          </div>
        </div>
      </div>

      {/* Email body */}
      <div className="p-8 bg-white">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>

        <div className="text-[15px] leading-6 text-gray-700 mb-8">{content}</div>

        {/* CTA button */}
        <a href={ctaUrl} className="inline-block px-6 py-3 bg-[#C080FF] text-white font-medium rounded-md text-center">
          {ctaText}
        </a>
      </div>

      {/* Footer */}
      <div className="p-4 bg-gray-100 text-center text-xs text-gray-500">
        <p>© 2025 TerraFusion. All rights reserved.</p>
        <p className="mt-1">123 Tech Park, Innovation City, CA 94103</p>
      </div>
    </div>
  )
}
