const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
dotenv.config();

const uploadRoutes = require('./routes/uploadRoutes');


const app = express();
app.use(cors());
app.use(express.json({ limit: '2gb'}));
app.use(express.urlencoded({ limit: '2gb', extended: true }));

app.use('/api',uploadRoutes);

const PORT = process.env.PORT;
app.listen(PORT, () => {
    console.log(`Server running successfully at port ${PORT} `);
})