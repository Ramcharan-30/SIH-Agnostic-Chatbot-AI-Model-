import dotenv from "dotenv";
import express from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";
import mongoose from "mongoose";

import rateLimiter from "./middleware/rateLimiter.js";
import errorHandler from "./middleware/errorHandler.js";
import chatRoutes from "./routes/chat.js";
import adminRoutes from "./routes/admin.js";

dotenv.config();

const app = express();

app.use(helmet());
app.use(
  cors({
    origin: "*",
    methods: ["GET", "POST"],
  })
);
app.use(express.json({ limit: "500kb" }));
app.use(morgan("dev"));
app.use(rateLimiter);

app.use("/", chatRoutes);
app.use("/admin", adminRoutes);

app.use(errorHandler);

if (!process.env.MONGODB_URI) {
  console.warn("MongoDB disabled: MONGODB_URI not found in environment variables");
} else {
  mongoose
    .connect(process.env.MONGODB_URI)
    .then(() => console.log("MongoDB connected"))
    .catch((err) => {
      console.error("MongoDB connection failed:", err.message);
      console.error("Continuing without database-backed chat logs.");
    });
}

export default app;
