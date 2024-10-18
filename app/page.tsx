import { YouTubeConverter } from '@/components/youtube-converter';
import { MP3List } from '@/components/mp3-list';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-8 text-center">
        YouTube to MP3 Converter2
      </h1>
      <YouTubeConverter />
      <MP3List />
    </div>
  );
}
