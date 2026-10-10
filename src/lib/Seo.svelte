<script lang="ts">
  import { SITE_NAME } from './site';
  import { absoluteUrl, serializeJsonLd, structuredData, type SeoPage } from './seo';

  let { page }: { page: SeoPage } = $props();
  const canonical = $derived(absoluteUrl(page.path));
  const image = $derived(absoluteUrl(page.image));
  const jsonLd = $derived(serializeJsonLd(structuredData(page)));
</script>

<svelte:head>
  <title>{page.title}</title>
  <meta name="description" content={page.description} />
  <link rel="canonical" href={canonical} />
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content={SITE_NAME} />
  <meta property="og:locale" content="ko_KR" />
  <meta property="og:title" content={page.title} />
  <meta property="og:description" content={page.description} />
  <meta property="og:url" content={canonical} />
  <meta property="og:image" content={image} />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content={page.imageAlt} />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content={page.title} />
  <meta name="twitter:description" content={page.description} />
  <meta name="twitter:image" content={image} />
  <meta name="twitter:image:alt" content={page.imageAlt} />
  {@html '<script type="application/ld+json">' + jsonLd + '</script>'}
</svelte:head>
