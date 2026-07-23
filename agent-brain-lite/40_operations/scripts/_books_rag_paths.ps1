# Dot-source: canonical books RAG data directory (local disk, not OneDrive).
if ($env:BOOKS_RAG_DATA_DIR) {
    $script:BooksRagDataDir = $env:BOOKS_RAG_DATA_DIR
} elseif ($IsWindows -or $env:OS -match 'Windows') {
    $script:BooksRagDataDir = 'C:\books_rag'
} else {
    $script:BooksRagDataDir = (Join-Path (Split-Path $PSScriptRoot -Parent -Parent) 'data\books_rag')
}
