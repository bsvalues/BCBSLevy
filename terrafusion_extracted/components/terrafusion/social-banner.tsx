interface SocialBannerProps {
  headline: string
  supportText: string
  url: string
}

export function SocialBanner({ headline, supportText, url }: SocialBannerProps) {
  return (
    <div className="w-full aspect-[3/1] max-w-[1500px] bg-gradient-to-r from-[#3DBE82] via-[#5A9BD5] to-[#C080FF] flex overflow-hidden relative">
      {/* Left third - hero product photo faded into gradient */}
      <div className="w-1/3 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent to-[#5A9BD5] z-10" />
        <div className="absolute inset-0 bg-gray-800 flex items-center justify-center text-white text-xl">
          [Product Photo]
        </div>
      </div>

      {/* Right two-thirds - content */}
      <div className="w-2/3 p-12 flex flex-col justify-center">
        {/* Monogram with orbital ring */}
        <div className="relative w-[120px] h-[120px] mb-8">
          <div className="absolute inset-0 rounded-xl border-2 border-[#1565C0] animate-spin-slow" />
          <div className="absolute inset-1 bg-[#2E7D32] rounded-lg flex items-center justify-center text-white font-bold text-4xl">
            TF
          </div>
        </div>

        <h1 className="text-4xl font-bold text-white mb-4">{headline}</h1>
        <p className="text-xl text-white/80 mb-6 max-w-2xl">{supportText}</p>
        <p className="text-white font-medium">{url}</p>
      </div>
    </div>
  )
}
