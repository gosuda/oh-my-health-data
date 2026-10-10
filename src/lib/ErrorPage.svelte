<script lang="ts">
  import { SITE_NAME } from '$lib/site';

  let { status = 404 }: { status?: number } = $props();
  const heading = $derived(status === 404 ? '페이지를 찾을 수 없습니다.' : '페이지를 불러오지 못했습니다.');
</script>

<svelte:head>
  <title>{heading} — {SITE_NAME}</title>
  <meta name="robots" content="noindex, follow" />
</svelte:head>

<main id="main" class="error-page container">
  <p class="error-status">{status}</p>
  <h1>{heading}</h1>
  <p>{status === 404 ? '주소를 다시 확인하거나 캠페인 첫 화면으로 이동해 주세요.' : '잠시 후 다시 시도하거나 캠페인 첫 화면으로 이동해 주세요.'}</p>
  <a class="button button-dark" href="/">캠페인 첫 화면으로 <span aria-hidden="true">↗</span></a>
</main>

<style>
  .error-page { min-height: 55vh; padding-block: clamp(64px, 12vw, 144px); }
  .error-status { margin-bottom: 20px; font-family: var(--display); font-size: clamp(48px, 9vw, 96px); font-weight: 800; line-height: 1; }
  h1 { margin-bottom: 20px; font-size: clamp(26px, 4vw, 48px); line-height: 1.3; }
  h1 + p { color: var(--muted); line-height: 1.8; }
  a { margin-top: 32px; }
</style>
