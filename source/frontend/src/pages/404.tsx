// frontend/src/pages/404.tsx
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/404')({
  component: NotFoundComponent,
});

function NotFoundComponent() {
  return <div>Page non trouvée</div>;
}
