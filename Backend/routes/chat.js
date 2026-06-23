import express from "express";
import multer from "multer";
import fs from "fs";
import { chat } from "../controller/chatController.js";
import botService from "../services/botService.js";

const router = express.Router();
const upload = multer({ dest: "uploads/" });

router.post("/api/chat", chat);

// Upload PDF/FAQ
router.post("/upload-faq", upload.single("file"), async (req, res) => {
    try {
        if (!req.file) return res.status(400).json({ error: "file required" });
        const meta = req.body.meta ? JSON.parse(req.body.meta) : {};
        const result = await botService.ingestFile(req.file.path, req.file.originalname, meta);
        fs.unlink(req.file.path, () => {});
        res.json({ ok: true, result });
    } catch (err) {
        res.status(500).json({ error: err.message || "upload failed" });
    }
});

export default router;
