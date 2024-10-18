"use client"

import { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from "@/components/ui/use-toast"

export function YouTubeConverter() {
  const [url, setUrl] = useState('');
  const [storage, setStorage] = useState('dropbox');
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, storage }),
      });
      
      if (response.ok) {
        toast({
          title: "Conversion started",
          description: "Your video is being converted and will be saved to your selected storage.",
        });
      } else {
        throw new Error('Conversion failed');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start conversion. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        type="url"
        placeholder="Enter YouTube URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        required
      />
      <Select value={storage} onValueChange={setStorage}>
        <SelectTrigger>
          <SelectValue placeholder="Select storage" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="dropbox">Dropbox</SelectItem>
          <SelectItem value="google-drive">Google Drive</SelectItem>
        </SelectContent>
      </Select>
      <Button type="submit" className="w-full">Convert and Download</Button>
    </form>
  );
}