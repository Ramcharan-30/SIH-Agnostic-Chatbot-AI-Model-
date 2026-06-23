import express from "express";
import ChatLog from "../models/chatLog.js";

const router = express.Router();

// List recent logs
router.get("/logs", async (req, res) => {
    const limit = Math.min(parseInt(req.query.limit || "100"), 1000);
    const logs = await ChatLog.find().sort({ createdAt: -1 }).limit(limit).lean();
    res.json({ count: logs.length, logs });
});

export default router;
