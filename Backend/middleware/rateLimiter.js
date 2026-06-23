import rateLimit from "express-rate-limit";

const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 min
  max: 30, // max requests per window
  message: { error: "Too many requests, please try again later." }
});

export default limiter;
