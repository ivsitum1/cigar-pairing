/** Ambient types for embedded browser PaddleOCR SDK. */
declare module "@paddleocr/paddleocr-js" {
  export class PaddleOCR {
    static create(opts?: Record<string, unknown>): Promise<PaddleOCR>;
    predict(
      input: File | Blob | ImageBitmap | HTMLCanvasElement | HTMLImageElement,
    ): Promise<unknown[]>;
  }
}
