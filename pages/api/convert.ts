import { NextApiRequest, NextApiResponse } from 'next';
import ytdl from 'ytdl-core';
import ffmpeg from 'fluent-ffmpeg';
import { Dropbox } from 'dropbox';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { url, storage } = req.body;

  try {
    // Download YouTube video
    const videoInfo = await ytdl.getInfo(url);
    const videoTitle = videoInfo.videoDetails.title.replace(/[^\w\s]/gi, '');
    const videoStream = ytdl(url, { quality: 'highestaudio' });

    // Convert to MP3
    const outputPath = path.join('/tmp', `${videoTitle}.mp3`);
    await new Promise((resolve, reject) => {
      ffmpeg(videoStream)
        .audioBitrate(128)
        .save(outputPath)
        .on('end', resolve)
        .on('error', reject);
    });

    // Upload to selected storage
    let fileUrl;
    if (storage === 'dropbox') {
      fileUrl = await uploadToDropbox(outputPath, videoTitle);
    } else if (storage === 'google-drive') {
      fileUrl = await uploadToGoogleDrive(outputPath, videoTitle);
    } else {
      throw new Error('Invalid storage option');
    }

    // Clean up temporary file
    fs.unlinkSync(outputPath);

    // Save MP3 info to database (implement this part)
    // saveMP3ToDatabase({ title: videoTitle, url: fileUrl, duration: videoInfo.videoDetails.lengthSeconds });

    res.status(200).json({ message: 'Conversion and upload successful', url: fileUrl });
  } catch (error) {
    console.error('Conversion failed:', error);
    res.status(500).json({ message: 'Conversion failed', error: error.message });
  }
}

async function uploadToDropbox(filePath: string, fileName: string): Promise<string> {
  const dbx = new Dropbox({ accessToken: process.env.DROPBOX_ACCESS_TOKEN });
  const fileContent = fs.readFileSync(filePath);
  const response = await dbx.filesUpload({ path: `/${fileName}.mp3`, contents: fileContent });
  const sharedLinkResponse = await dbx.sharingCreateSharedLink({ path: response.result.path_lower });
  return sharedLinkResponse.result.url;
}

async function uploadToGoogleDrive(filePath: string, fileName: string): Promise<string> {
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_APPLICATION_CREDENTIALS,
    scopes: ['https://www.googleapis.com/auth/drive.file'],
  });
  const drive = google.drive({ version: 'v3', auth });
  const response = await drive.files.create({
    requestBody: {
      name: `${fileName}.mp3`,
      mimeType: 'audio/mpeg',
    },
    media: {
      mimeType: 'audio/mpeg',
      body: fs.createReadStream(filePath),
    },
  });
  await drive.permissions.create({
    fileId: response.data.id,
    requestBody: {
      role: 'reader',
      type: 'anyone',
    },
  });
  const fileResponse = await drive.files.get({
    fileId: response.data.id,
    fields: 'webViewLink',
  });
  return fileResponse.data.webViewLink;
}