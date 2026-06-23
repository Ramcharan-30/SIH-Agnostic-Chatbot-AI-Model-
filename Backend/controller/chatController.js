import ChatLog from "../models/chatLog.js";
import { ensureSessionId } from "../utils/session.js";
import botService from "../services/botService.js";

const CONF_THRESH = parseFloat(process.env.CONFIDENCE_THRESHOLD || "0.6");
const ADMIN_CONTACT = process.env.ADMIN_CONTACT || "admin@college.edu";

export async function chat(req, res, next) {
    try {
        const { userId, message, sessionId, language } = req.body;
        if (!message) return res.status(400).json({ error: "message required" });

        const sid = ensureSessionId(sessionId);

        // save incoming
        const incoming = await ChatLog.create({
            userId,
            sessionId: sid,
            message,
            createdAt: new Date()
        });

        // call python bot
        const botResp = await botService.sendMessage({ userId, message, sessionId: sid, language });

        const answer = botResp.answer || "Sorry, I couldn’t find an answer.";
        const confidence = botResp.confidence ?? 0;
        let needsHuman = botResp.needsHuman || false;

        if (confidence < CONF_THRESH) needsHuman = true;

        // update log
        incoming.response = answer;
        incoming.confidence = confidence;
        incoming.needsHuman = needsHuman;
        incoming.language = botResp.language || language;
        incoming.sourceDocs = botResp.sources || [];
        await incoming.save();

        const response = { answer, sessionId: sid, confidence, needsHuman, sources: botResp.sources || [] };
        if (needsHuman) response.humanContact = ADMIN_CONTACT;

        res.json(response);
    } catch (err) { next(err); }
}
