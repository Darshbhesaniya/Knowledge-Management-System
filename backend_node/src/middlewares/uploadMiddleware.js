const multer = require('multer');

 // Allowed MIME types
    const allowedMimeTypes = [
        // PDF
        'application/pdf',
        // Microsoft Word
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        // CSV
        'text/csv',
        'application/csv',
        // Markdown
        'text/markdown',
        'text/x-markdown',
        // Text files
        'text/plain',
        // Additional common types
        'application/rtf',
        'application/vnd.oasis.opendocument.text'
    ];

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null,"uploads/");
    },
});

const fileFilter = (req, file, cb) => {
    if (allowedMimeTypes.includes(file.mimetype)) {
        cb(null, true);
    } else {
        cb(new Error(`File type ${file.mimetype} is not allowed. Allowed types: PDF, DOC/DOCX, CSV, Markdown, TXT`), false);
    }
};

const upload = multer({
    storage,
    fileFilter,
    limits: {
        fileSize: 500 * 1024 * 1024,
    },
});

module.exports = {
    multipleFiles: upload.array('files', 7),
}