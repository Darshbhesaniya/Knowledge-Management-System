const { randomUUID } = require('crypto')
const fs = require('fs').promises;

const minioRepository = require('../repositories/minioRepository');

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