"use client"

import { useState, useEffect } from "react"
import { QrCode, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface BarcodeScannerProps {
  isOpen: boolean
  onClose: () => void
  onCodeScanned: (code: string) => void
}

export function BarcodeScanner({ isOpen, onClose, onCodeScanned }: BarcodeScannerProps) {
  const [permission, setPermission] = useState<boolean | null>(null)
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Mock scanning for demo purposes
  const simulateScan = () => {
    // In a real app, this would be replaced with actual barcode/QR scanning logic
    const mockCodes = ["PS-001", "RAM-8G", "SSD-500", "NSW-24", "RW-001"]
    const randomCode = mockCodes[Math.floor(Math.random() * mockCodes.length)]
    onCodeScanned(randomCode)
    onClose()
  }

  useEffect(() => {
    if (isOpen) {
      // In a real implementation, we would request camera access and set up scanning
      // For this demo, we'll just simulate permission being granted
      setPermission(true)
      setErrorMessage(null)
    } else {
      // Clean up camera stream when dialog closes
      if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop())
        setCameraStream(null)
      }
    }
  }, [isOpen, cameraStream])

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Scan Barcode or QR Code</DialogTitle>
          <DialogDescription>Position the barcode or QR code in the center of the camera view.</DialogDescription>
        </DialogHeader>

        <div className="flex justify-center py-6">
          {permission === true ? (
            <div className="relative w-full max-w-sm aspect-video bg-muted rounded-md flex items-center justify-center">
              {/* This would be a video element in a real implementation */}
              <div className="border-2 border-dashed border-primary/50 w-2/3 h-2/3 flex items-center justify-center">
                <QrCode className="h-16 w-16 text-primary/30" />
              </div>
            </div>
          ) : permission === false ? (
            <div className="text-center p-4 bg-red-50 dark:bg-red-950/20 rounded-md">
              <p className="text-red-600">Camera access denied. Please enable camera access to scan codes.</p>
            </div>
          ) : errorMessage ? (
            <div className="text-center p-4 bg-red-50 dark:bg-red-950/20 rounded-md">
              <p className="text-red-600">{errorMessage}</p>
            </div>
          ) : (
            <div className="flex items-center justify-center h-40">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}
        </div>

        <DialogFooter className="flex justify-between sm:justify-between">
          <Button variant="outline" onClick={onClose}>
            <X className="mr-2 h-4 w-4" />
            Cancel
          </Button>
          <Button onClick={simulateScan}>Simulate Scan</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
