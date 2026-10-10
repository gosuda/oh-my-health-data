<script lang="ts">
  let year = $state('');
  const years = Array.from({ length: 10 }, (_, index) => String(2015 + index));
  let isInRange = $derived(years.includes(year));
</script>

<section id="check" class="yc-section" aria-labelledby="yc-title">
  <div class="yc-container">
    <div class="yc-copy">
      <h2 id="yc-title">병무청 신검,<br />언제 받았나요?</h2>
      <p class="yc-description">
        공개된 의료데이터 결합 연구의 제공 기간과<br class="yc-desktop-break" />
        검사 연도를 비교해 보세요.
      </p>
    </div>

    <div class="yc-panel">
      <div class="yc-year-band">
        <span class="yc-band-label">공개된 제공 대상 기간</span>
        <strong>2015<span aria-hidden="true">—</span><span class="yc-sr-only">년부터</span>2024<span class="yc-sr-only">년까지</span></strong>
      </div>

      <div class="yc-input-area">
        <label for="yc-exam-year">신검 받은 연도</label>
        <select id="yc-exam-year" class="yc-select" aria-label="병무청 신검 연도" bind:value={year}>
          <option value="" disabled>연도를 선택해 주세요</option>
          <option value="before">2014년 이전</option>
          {#each years as optionYear}
            <option value={optionYear}>{optionYear}년</option>
          {/each}
          <option value="after">2025년 이후</option>
          <option value="unknown">기억나지 않아요</option>
        </select>
        <p class="yc-privacy">선택한 연도는 저장하거나 전송하지 않습니다.</p>
      </div>

      <div class="yc-result" class:yc-result-visible={year !== ''} role="status" aria-live="polite" aria-atomic="true">
        {#if year !== ''}
          {#if isInRange}
            <p class="yc-result-title"><strong>{year}년 검사, 공개된 제공 대상 기간에 해당합니다.</strong></p>
            <p class="yc-result-copy">병무청은 2015~2024년 검사 데이터를 의료데이터 결합 연구에 제공합니다.</p>
            <p class="yc-scope">검사 연도와 공개 기간을 비교한 결과입니다. 개인별 제공 여부는 병무청 확인이 필요합니다.</p>
          {:else if year === 'unknown'}
            <p class="yc-result-title"><strong>연도가 기억나지 않아도, 정보의 쓰임은 확인할 수 있습니다.</strong></p>
          {:else}
            <p class="yc-result-title"><strong>공개된 2015~2024년 제공 기간 밖입니다.</strong></p>
            <p class="yc-result-copy">이 결과는 해당 제공 건의 기간 비교입니다. 원본 보관과 다른 연구 활용은 별도로 확인하세요.</p>
          {/if}
          <div class="yc-links">
            <a href="#story">제공한 정보 보기 <span aria-hidden="true">↓</span></a>
            <a href="/sources/#research">공식 자료 <span aria-hidden="true">↗</span></a>
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>

<style>
  .yc-section {
    color: var(--ink, #1c211c);
    background: var(--paper, #f3f1e8);
    padding-block: 64px;
    border-bottom: 1px solid var(--line, #c9cbc1);
    scroll-margin-top: 20px;
  }

  .yc-container {
    width: min(1320px, calc(100% - 112px));
    margin-inline: auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(36px, 6vw, 92px);
    align-items: start;
  }

  .yc-copy { padding-top: 8px; }
  .yc-copy h2 { margin: 0 0 18px; font-size: clamp(29px, 3.3vw, 47px); font-weight: 850; letter-spacing: -.065em; line-height: 1.35; word-break: keep-all; }
  .yc-description { font-size: 14px; line-height: 1.85; color: var(--muted, #656a60); }
  .yc-panel { min-width: 0; border: 1px solid var(--ink, #1c211c); }
  .yc-year-band { padding: 18px 25px 20px; display: flex; align-items: center; justify-content: space-between; gap: 18px; background: var(--acid, #e5ff36); border-bottom: 1px solid var(--ink, #1c211c); }
  .yc-band-label { display: block; max-width: 108px; padding: 7px 9px; background: var(--ink, #1c211c); color: var(--acid, #e5ff36); font-size: 10px; font-weight: 650; line-height: 1.6; word-break: keep-all; }
  .yc-year-band > strong { display: flex; align-items: center; gap: 9px; font-family: var(--display, 'Arial Narrow', sans-serif); font-size: clamp(35px, 4vw, 54px); font-weight: 800; letter-spacing: -.025em; line-height: 1; white-space: nowrap; }
  .yc-year-band > strong > span[aria-hidden] { font-size: .65em; font-weight: 700; }
  .yc-input-area { padding: 24px 25px; }
  .yc-input-area label { display: block; font-size: 12px; font-weight: 750; margin-bottom: 10px; }
  .yc-select { display: block; width: 100%; min-width: 0; min-height: 52px; padding: 12px 14px; border: 1px solid var(--ink, #1c211c); border-radius: 0; font: inherit; font-size: 14px; color: var(--ink, #1c211c); background: var(--paper, #f3f1e8); cursor: pointer; }
  .yc-select:focus-visible, .yc-links a:focus-visible { outline: 3px solid #718100; outline-offset: 4px; }
  .yc-privacy { margin-top: 11px; font-size: 10px; line-height: 1.7; color: var(--muted, #656a60); }
  .yc-result-visible { border-top: 1px solid var(--line, #c9cbc1); padding: 23px 25px 24px; }
  .yc-result-title { font-size: 18px; line-height: 1.6; letter-spacing: -.035em; word-break: keep-all; overflow-wrap: anywhere; }
  .yc-result-title strong { font-weight: 800; }
  .yc-result-copy { margin-top: 11px; font-size: 13px; line-height: 1.85; word-break: keep-all; }
  .yc-scope { margin-top: 13px; font-size: 11px; line-height: 1.8; color: var(--muted, #656a60); word-break: keep-all; }
  .yc-links { display: flex; flex-wrap: wrap; gap: 12px 24px; margin-top: 22px; }
  .yc-links a { display: inline-flex; align-items: center; gap: 10px; color: inherit; font-size: 12px; font-weight: 700; padding-block: 4px; border-bottom: 1px solid currentColor; text-decoration: none; }
  .yc-links a:hover { background: var(--acid, #e5ff36); }
  .yc-sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }

  @media (max-width: 800px) {
    .yc-container { width: calc(100% - 44px); grid-template-columns: 1fr; gap: 27px; }
    .yc-year-band { padding-inline: 18px; gap: 12px; }
    .yc-year-band > strong { font-size: 38px; gap: 6px; }
    .yc-band-label { max-width: 90px; font-size: 9px; padding: 6px 7px; }
    .yc-input-area, .yc-result-visible { padding: 21px 18px; }
    .yc-desktop-break { display: none; }
  }

  @media (max-width: 560px) {
    .yc-section { padding-block: 44px; }
    .yc-container { width: calc(100% - 40px); grid-template-columns: 1fr; gap: 27px; }
    .yc-copy { padding-top: 0; }
    .yc-copy h2 { font-size: 33px; margin: 0 0 15px; }
    .yc-description { font-size: 13px; }
    .yc-year-band { padding: 17px 18px; gap: 10px; }
    .yc-band-label { max-width: 92px; }
    .yc-year-band > strong { font-size: 43px; }
    .yc-result-title { font-size: 17px; }
    .yc-result-copy { font-size: 12px; }
    .yc-scope { font-size: 10px; }
    .yc-links { column-gap: 20px; }
    .yc-links a { font-size: 11px; }
  }

  @media (max-width: 360px) {
    .yc-year-band > strong { font-size: 36px; }
    .yc-year-band { padding-inline: 15px; }
    .yc-copy h2 { font-size: 30px; }
  }
</style>
