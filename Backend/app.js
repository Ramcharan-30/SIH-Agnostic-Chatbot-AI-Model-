import dotenv from "dotenv";
import express from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";
import mongoose from "mongoose";

//puneethrayapudi16_db_user
//Zm7ucvmCe7iLbrR3

 
import rateLimiter from "./middleware/rateLimiter.js";
import errorHandler from "./middleware/errorHandler.js";

import chatRoutes from "./routes/chat.js";
import adminRoutes from "./routes/admin.js";

dotenv.config();

const app = express();

// security & middleware
app.use(helmet());
app.use(cors({
  origin: "*", // later restrict to frontend URL
  methods: ["GET", "POST"]
}));
app.use(express.json({ limit: "500kb" }));
app.use(morgan("dev"));
app.use(rateLimiter);

// routes
app.use("/", chatRoutes);
app.use("/admin", adminRoutes);

// error handler
app.use(errorHandler);

// connect mongo
if (!process.env.MONGODB_URI) {
    console.error("❌ MONGODB_URI not found in environment variables");
    process.exit(1);
}

mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
.then(() => console.log("✅ MongoDB connected"))
.catch(err => {
    console.error("❌ MongoDB connection failed:", err.message);
    console.error("Connection string format check: Ensure no angle brackets around password");
    process.exit(1);
});

export default app;