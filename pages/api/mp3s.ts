import { NextApiRequest, NextApiResponse } from 'next';

// This is a mock implementation. In a real application, you would fetch this data from a database.
const mockMP3s = [
  { id: '1', title: 'Song 1', duration: '3:45', url: 'https://example.com/song1.mp3' },
  { id: '2', title: 'Song 2', duration: '4:20', url: 'https://example.com/song2.mp3' },
  { id: '3', title: 'Song 3', duration: '2:55', url: 'https://example.com/song3.mp3' },
];

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    // In a real application, you would fetch the MP3 list from your database here
    res.status(200).json(mockMP3s);
  } else {
    res.setHeader('Allow', ['GET']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}