import Image from "next/image"

interface BrandAssetProps {
  variant?: "default" | "app" | "seal" | "square"
  size?: "sm" | "md" | "lg" | "xl"
  className?: string
}

const sizeMap = {
  sm: 48,
  md: 96,
  lg: 144,
  xl: 192,
}

export function TerraFusionLogo({ variant = "default", size = "md", className = "" }: BrandAssetProps) {
  const dimensions = sizeMap[size]

  // URLs for the different logo variants
  const logoUrls = {
    default: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-kxsGwXzvQnYOMtqRmB0Buf9j7HtSxb.png",
    app: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-0h7tzBkj83NtRDd6ZwGUXg67nKeW5j.png", // Using the first image as fallback
    seal: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-0h7tzBkj83NtRDd6ZwGUXg67nKeW5j.png", // Using the first image as fallback
    square: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-0h7tzBkj83NtRDd6ZwGUXg67nKeW5j.png", // Using the first image as fallback
  }

  return (
    <div className={`relative ${className}`} style={{ width: dimensions, height: dimensions }}>
      <Image
        src={logoUrls[variant] || "/placeholder.svg"}
        alt="TerraFusion Logo"
        width={dimensions}
        height={dimensions}
        className="object-contain"
      />
    </div>
  )
}

export function TerraFusionLogoSet() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="flex flex-col items-center">
        <Image
          src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-0h7tzBkj83NtRDd6ZwGUXg67nKeW5j.png"
          alt="TerraFusion Logo Variations"
          width={500}
          height={500}
          className="object-contain"
        />
      </div>
    </div>
  )
}
