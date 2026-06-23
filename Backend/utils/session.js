import { v4 as uuidv4 } from "uuid";

export function ensureSessionId(sid) {
    return sid || uuidv4();
}
