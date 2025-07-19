'use client';
import Image from 'next/image';

type AvenLogoProps = {
  className?: string;
};

export default function AvenLogo({ className = '' }: AvenLogoProps) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <Image src="/aven.svg" alt="Aven" width={28} height={28} />
      <span className="text-lg font-semibold text-black">Aven</span>
    </div>
  );
}
