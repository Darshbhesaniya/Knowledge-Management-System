const Minio = require('minio');
const fs = require('fs');

const minioClient = new Minio.Client({
    endPoint: process.env.MINIO_ENDPOINT,
    port: parseInt(process.env.MINIO_PORT, 10),
    useSSL: process.env.MINIO_USE_SSL === 'true',
    accessKey: process.env.MINIO_ACCESS_KEY,
    secretKey: process.env.MINIO_SECRET_KEY
});

const bucketName = process.env.MINIO_BUCKET_NAME;

minioClient.bucketExists(bucketName, function(err, exists){
    if(err){
        return console.log(err);
    }
    if(!exists){
        minioClient.makeBucket(bucketName, 'us-east-1', function(err){
            if(err){
               console.log("MineIo Bucker CreationError: ",err);
            } else {
                console.log("✅ Bucket Created Successfully ");
            }
        });
    }
});

const uploadFileToMinio = async (fileName, filePath, size, contentType) => {
    
    return await minioClient.fPutObject(
        bucketName,
        fileName,
        filePath,
        {
            'Content-Type': contentType
        }
    );
};

module.exports = {
    uploadFileToMinio
}