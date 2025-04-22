import Image from "next/image"

interface DashboardCardProps {
  title: string
  metric: string | number
  description?: string
}

export function DashboardCard({ title, metric, description }: DashboardCardProps) {
  return (
    <div
      className="w-80 p-8 rounded-xl relative bg-[#001529]/90 border border-[#00e5ff]/20"
      style={{
        boxShadow: "0 0 20px rgba(0,229,255,0.1)",
      }}
    >
      {/* Tiny TerraFusion watermark */}
      <div className="absolute top-3 left-3 w-4 h-4 opacity-10">
        <Image
          src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png"
          alt="TerraFusion Logo"
          width={16}
          height={16}
          className="object-contain"
        />
      </div>

      <div className="space-y-2">
        <h3 className="text-sm font-medium text-[#00e5ff]/70">{title}</h3>

        {/* Large metric with fluid scaling */}
        <p className="text-[clamp(2.6rem,2vw+1.4rem,4rem)] font-bold text-white">{metric}</p>

        {description && <p className="text-sm text-[#00e5ff]/50">{description}</p>}
      </div>
    </div>
  )
}
