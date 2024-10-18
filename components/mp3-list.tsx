"use client"

import { useState, useEffect } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Play } from 'lucide-react';

interface MP3File {
  id: string;
  title: string;
  duration: string;
  url: string;
}

export function MP3List() {
  const [mp3s, setMP3s] = useState<MP3File[]>([]);

  useEffect(() => {
    fetchMP3s();
  }, []);

  const fetchMP3s = async () => {
    try {
      const response = await fetch('/api/mp3s');
      if (response.ok) {
        const data = await response.json();
        setMP3s(data);
      }
    } catch (error) {
      console.error('Failed to fetch MP3s:', error);
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold mb-4">Your MP3 Files</h2>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Duration</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {mp3s.map((mp3) => (
            <TableRow key={mp3.id}>
              <TableCell>{mp3.title}</TableCell>
              <TableCell>{mp3.duration}</TableCell>
              <TableCell>
                <Button variant="outline" size="icon" onClick={() => window.open(mp3.url, '_blank')}>
                  <Play className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}