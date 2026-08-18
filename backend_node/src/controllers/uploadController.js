const uploadService = require('../services/uploadService');

const handleMultipleFilesUpload = async (req, res) => {
    try {
        if(!req.files || req.files.length === 0){
            return res.status(400).json({ error: 'No File uploaded'})
        }

        const savedFilename = await uploadService.processMultipleFiles(req.files);

        res.status(200).json({
            message: 'File Uploaded Successfully',
            fileName: savedFilename
        });
        
    } catch (error) {
        console.log("Upload Error: ",error);
        res.status(500).json({
            error: "Internal Server Error During file Uploads "
        });
    }
};

module.exports = {
    handleMultipleFilesUpload
}