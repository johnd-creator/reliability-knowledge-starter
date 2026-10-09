/** Bounded bytes and one whole-operation deadline; never parse before capping. */
export class HttpLimitError extends Error {
  constructor(readonly code: 'BODY_TOO_LARGE' | 'DEADLINE_EXCEEDED') { super(code); }
}
async function nextChunk(reader: ReadableStreamDefaultReader<Uint8Array>, signal: AbortSignal) {
  if (signal.aborted) throw new HttpLimitError('DEADLINE_EXCEEDED');
  let onAbort: () => void = () => {};
  const aborted = new Promise<never>((_, reject) => {
    onAbort = () => reject(new HttpLimitError('DEADLINE_EXCEEDED'));
    signal.addEventListener('abort', onAbort, {once: true});
    if (signal.aborted) onAbort();
  });
  try { return await Promise.race([reader.read(), aborted]); }
  finally { signal.removeEventListener('abort', onAbort); }
}
export async function readBounded(stream: ReadableStream<Uint8Array> | null, limit: number, signal: AbortSignal): Promise<Uint8Array<ArrayBuffer>> {
  if (!Number.isSafeInteger(limit) || limit < 1) throw new Error('INVALID_BODY_LIMIT');
  if (!stream) return new Uint8Array();
  const reader = stream.getReader(); const chunks: Uint8Array[] = []; let total = 0;
  try {
    for (;;) {
      const {done, value} = await nextChunk(reader, signal);
      if (done) break;
      total += value.byteLength;
      if (total > limit) throw new HttpLimitError('BODY_TOO_LARGE');
      chunks.push(value);
    }
    const result = new Uint8Array(total); let offset = 0;
    for (const chunk of chunks) { result.set(chunk, offset); offset += chunk.byteLength; }
    return result;
  } catch (error) {
    void reader.cancel().catch(() => {});
    throw error;
  } finally { try { reader.releaseLock(); } catch {} }
}
