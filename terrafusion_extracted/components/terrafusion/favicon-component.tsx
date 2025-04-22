export function FaviconComponent() {
  return (
    <div className="p-8 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-6">Favicon & PWA Icon Set</h2>

      <div className="grid grid-cols-3 gap-8">
        <div className="flex flex-col items-center">
          <div className="w-16 h-16 bg-[#2E7D32] rounded-md shadow-md flex items-center justify-center text-white font-bold text-xs">
            TF
          </div>
          <p className="mt-2 text-sm text-gray-500">16×16 .ico</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-24 h-24 bg-[#2E7D32] rounded-md shadow-md flex items-center justify-center text-white font-bold text-lg">
            TF
          </div>
          <p className="mt-2 text-sm text-gray-500">192×192 PNG</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-32 h-32 bg-[#2E7D32] rounded-md shadow-md flex items-center justify-center text-white font-bold text-2xl">
            TF
          </div>
          <p className="mt-2 text-sm text-gray-500">512×512 PNG</p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-gray-100 rounded-md">
        <h3 className="text-sm font-medium mb-2">manifest.webmanifest</h3>
        <pre className="text-xs bg-gray-800 text-white p-3 rounded overflow-x-auto">
          {`{
  "name": "TerraFusion",
  "short_name": "TF",
  "icons": [
    {
      "src": "/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "theme_color": "#1565C0",
  "background_color": "#ffffff",
  "display": "standalone"
}`}
        </pre>
      </div>
    </div>
  )
}
