import express from 'express';
import multer from 'multer';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import cors from 'cors';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());

// Serve output videos statically
app.use('/output-videos', express.static(path.join(__dirname, '..', 'output_videos')));

// Serve live frames for real-time streaming
const liveFramesDir = path.join(__dirname, '..', 'live_frames');
if (!fs.existsSync(liveFramesDir)) {
    fs.mkdirSync(liveFramesDir, { recursive: true });
}
app.use('/live-frame', express.static(liveFramesDir));

// Endpoint to get latest live frame
app.get('/live-frame-latest', (req, res) => {
    const framePath = path.join(liveFramesDir, 'current.jpg');
    if (fs.existsSync(framePath)) {
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
        res.sendFile(framePath);
    } else {
        res.status(404).send('No frame yet');
    }
});

// Configure multer for file uploads - save to input_videos folder
const inputVideosDir = path.join(__dirname, '..', 'input_videos');
if (!fs.existsSync(inputVideosDir)) {
    fs.mkdirSync(inputVideosDir, { recursive: true });
}

const storage = multer.diskStorage({
    destination: (req, file, cb) => cb(null, inputVideosDir),
    filename: (req, file, cb) => cb(null, `upload_${Date.now()}_${file.originalname}`)
});
const upload = multer({ storage });

app.post('/analyze', upload.single('video'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No video uploaded');
    }

    const videoPath = req.file.path;
    const ext = path.extname(req.file.originalname) || '.mp4';
    const newPath = videoPath.replace(/\.[^.]*$/, '') + ext;
    if (videoPath !== newPath) {
        fs.renameSync(videoPath, newPath);
    }

    // Clear previous live frames
    const currentFrame = path.join(liveFramesDir, 'current.jpg');
    if (fs.existsSync(currentFrame)) {
        fs.unlinkSync(currentFrame);
    }

    // Set up SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Use venv python executable
    const pythonExecutable = path.resolve(__dirname, '..', 'venv', 'bin', 'python');
    const pythonProcess = spawn(pythonExecutable, ['main.py', '--kimi', '--no-preview', '--live-stream', '--video', newPath], {
        cwd: path.join(__dirname, '..'),
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    });

    pythonProcess.stdout.on('data', (data) => {
        res.write(data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
        res.write(data.toString());
    });

    pythonProcess.on('close', (code) => {
        // Find the output video file
        const outputDir = path.join(__dirname, '..', 'output_videos');
        if (fs.existsSync(outputDir)) {
            const files = fs.readdirSync(outputDir)
                .filter(f => f.startsWith('analysis_') && f.endsWith('.mp4'))
                .map(f => ({ name: f, time: fs.statSync(path.join(outputDir, f)).mtime }))
                .sort((a, b) => b.time - a.time);

            if (files.length > 0) {
                const latestVideo = files[0].name;
                res.write(`\n===VIDEO_OUTPUT===${latestVideo}===\n`);
            }
        }
        res.write(`\n=== Analysis complete (exit code: ${code}) ===\n`);
        res.end();
    });

    pythonProcess.on('error', (err) => {
        res.write(`Error: ${err.message}\n`);
        res.end();
    });
});

const PORT = 5001;
app.listen(PORT, () => {
    console.log(`Analysis server running on http://localhost:${PORT}`);
});
