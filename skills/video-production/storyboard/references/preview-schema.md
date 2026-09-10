# Storyboard preview schema

The storyboard manifest should be JSON (or a directly equivalent TypeScript object) with stable IDs and relative asset paths.

```ts
type StoryboardManifest = {
  version: 1;
  title: string;
  source: {
    type: "script" | "video";
    path?: string;
    transcriptPath?: string;
    durationInSeconds?: number;
  };
  overviewImage?: string;
  beats: StoryboardBeat[];
};

type StoryboardBeat = {
  id: string;
  index: number;
  title: string;
  startSeconds?: number;
  endSeconds?: number;
  scriptRange?: string;
  transcript: string;
  visualObjective: string;
  motionDescription: string;
  useSourceVideo: boolean;
  imagePath?: string;
  implementationPath?: string;
  renderedPreviewPath?: string;
  status: "proposed" | "approved" | "built" | "needs-review";
  notes?: string;
};
```

Beat IDs should remain unchanged when images or implementation files are regenerated. Use predictable paths such as `beats/beat-01/board.png`, `beats/beat-01/scene.tsx`, and `beats/beat-01/render.png`.
