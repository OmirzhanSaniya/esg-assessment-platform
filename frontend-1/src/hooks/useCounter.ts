import { useEffect, useRef, useState } from 'react';

interface UseCounterOptions {
  target: number;
  duration?: number;   
  decimals?: number;  
  threshold?: number;  
}

function easeOutCubic(t: number): number {
  return 1 - Math.pow(1 - t, 3);
}


export function useCounter({
  target,
  duration = 3000,
  decimals = 0,
  threshold = 0.4,
}: UseCounterOptions) {
  const ref = useRef<HTMLElement | null>(null);
  const [value, setValue] = useState<string>((0).toFixed(decimals));
  const animatedRef = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !animatedRef.current) {
            animatedRef.current = true;
            const start = performance.now();

            const tick = (now: number) => {
              const progress = Math.min((now - start) / duration, 1);
              const eased = easeOutCubic(progress);
              setValue((target * eased).toFixed(decimals));

              if (progress < 1) {
                requestAnimationFrame(tick);
              } else {
                setValue(target.toFixed(decimals));
              }
            };

            requestAnimationFrame(tick);
            observer.unobserve(el);
          }
        });
      },
      { threshold }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [target, duration, decimals, threshold]);

  return { ref, value };
}