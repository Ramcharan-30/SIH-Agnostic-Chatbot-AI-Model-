import mongoose from "mongoose";

const ChatLogSchema = new mongoose.Schema({
    userId: { type: String, index: true },
    sessionId: { type: String, index: true },
    message: String,
    response: String,
    confidence: Number,
    needsHuman: { type: Boolean, default: false },
    language: String,
    sourceDocs: Array,
    createdAt: { type: Date, default: Date.now },
    metadata: Object
});

// Auto-delete logs after N days
ChatLogSchema.index(
    { createdAt: 1 },
    { expireAfterSeconds: 60 * 60 * 24 * parseInt(process.env.LOG_RETENTION_DAYS || "90") }
);

const ChatLog = mongoose.model("ChatLog", ChatLogSchema);

export default ChatLog;
