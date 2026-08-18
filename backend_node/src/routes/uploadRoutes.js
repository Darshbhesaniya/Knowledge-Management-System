const express = require('express');
const router = express.Router();

const uploadController = require('../controllers/uploadController');
const uploadMiddleware = require('../middlewares/uploadMiddleware');

router.post('/uploads',uploadMiddleware.multipleFiles, uploadController.handleMultipleFilesUpload)

module.exports = router;