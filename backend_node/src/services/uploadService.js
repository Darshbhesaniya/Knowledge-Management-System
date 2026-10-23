const { randomUUID } = require('crypto')
const fs = require('fs').promises;
const { Queue } = require('bullmq');

const minioRepository = require('../repositories/minioRepository');

const documentQueue = new Queue('document-processing-queue', {
    connection: { host: 'localhost', port: 6379 }
})

const processMultipleFiles = async (files) => {
    const uploadFileNames = [];

    await Promise.all(
        files.map(async (file) => {

            const fileName = `${randomUUID()}-${file.originalname}`;

            try {
                await minioRepository.uploadFileToMinio(
                fileName,
                file.path,
                file.mimetype
            );

            // Add file in Redis Queue
            await documentQueue.add('process-pdf-job', {
                fileName: fileName,
                bucketName: process.env.MINIO_BUCKET_NAME
            });
            console.log(`Job added to Queue for ${fileName}`);
        
            uploadFileNames.push(fileName);
            } catch (error) {
                console.log(`Error Uploading ${fileName}: `, error);
                throw error;
            } finally {
                try {
                    await fs.unlink(file.path);
                    console.log(`Deleted Temporary file: ${file.path}`);
                    
                } catch (unlinkError) {
                    console.log(`failed to delete local file: ${file.path}, unlinkError`);
                    
                }
            }

        })
    );

    return uploadFileNames;
};

module.exports = {
    processMultipleFiles
}