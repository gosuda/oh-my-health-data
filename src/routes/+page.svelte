<script lang="ts">
  import { onMount } from 'svelte';
  import HeroArtwork from '$lib/HeroArtwork.svelte';
  import YearCheck from '$lib/YearCheck.svelte';
  import SkillPromo from '$lib/SkillPromo.svelte';
  import Mark from '$lib/Mark.svelte';
  import Seo from '$lib/Seo.svelte';
  import { SEO_PAGES, absoluteUrl } from '$lib/seo';
  import { downloadPoster, type PosterTheme } from '$lib/poster';

  const demands = [
    { id: 'disclosure' as PosterTheme, number: '01', short: '사용처 공개', title: '누구에게 무엇을\n제공했는지 공개하라.', lines: ['내 건강정보.', '어디에 썼는지', '공개하라.'], description: '어떤 정보를, 누구에게, 무슨 목적으로 제공했는지 당사자가 알 수 있어야 합니다.', route: '정보공개포털', url: 'https://www.open.go.kr/', letter: '병역판정 건강정보의 연구 제공 내역 공개를 청구합니다.\n\n1. 제공한 데이터의 전체 항목 정의서와 코드북\n2. 제공받은 기관 및 최종 연구수행기관, 연구 목적과 제공 기간\n3. 제공·결합·반출에 관한 승인 문서와 이용 조건\n\n현재 보유·관리하는 문서의 전자파일 공개를 요청합니다. 비공개 또는 부분공개하는 경우 항목별 법적 근거와 사유를 밝혀 주십시오.' },
    { id: 'retention' as PosterTheme, number: '02', short: '삭제 기준 공개', title: '보존 이유와\n삭제 기준을 밝혀라.', lines: ['내 건강정보.', '언제 지우는지', '밝혀라.'], description: '원본과 사본, 백업을 언제까지 보관하는지 밝히고, 필요가 끝난 정보는 삭제해야 합니다.', route: '정보공개포털', url: 'https://www.open.go.kr/', letter: '병역판정 건강정보의 보존·파기 기준 공개를 청구합니다.\n\n1. 수검자 파일, 검사결과, 진료기록 스캔본, 의료영상, 백업별 보존기간과 법적 근거\n2. 영구 보유 항목과 기간을 정하여 보유하는 항목의 구분\n3. 연구용 사본·결합정보·모델 등 결과물의 보존 및 파기 기준\n4. 기간 연장 및 실제 파기 이행을 확인할 수 있는 문서\n\n현재 보유·관리하는 문서의 전자파일 공개를 요청합니다. 자료별 보존기간의 기산점과 예외 기준도 포함해 주십시오.' },
    { id: 'choice' as PosterTheme, number: '03', short: '선택권 보장', title: '연구 활용에\n선택권을 보장하라.', lines: ['내 몸의 정보다.', '내 선택도', '있어야 한다.'], description: '의무적으로 제출한 건강정보. 연구에 쓰이는 과정에는 당사자의 선택이 반영되어야 합니다.', route: '국민신문고', url: 'https://www.epeople.go.kr/', letter: '병역판정 건강정보의 연구 활용에 대한 정보주체의 선택권 보장을 요구합니다.\n\n1. 장래 연구 활용에서 제외해 달라는 요청을 수용하는 절차가 있는지 답변해 주십시오.\n2. 절차가 없다면 연구 활용 거부권과 신청 절차를 마련할 것을 요구합니다.\n3. 연구 이용기관·목적·제공 항목·보존기간을 당사자가 쉽게 확인할 수 있는 공개 체계를 마련해 주십시오.\n\n각 요구에 대한 현행 정책과 개선 계획을 구분하여 답변해 주십시오.' }
  ];
  let selected = $state<PosterTheme>('choice');
  const current = $derived(demands.find((d) => d.id === selected)!);
  let letterOpen = $state(false);
  let exporting = $state(false);
  let notice = $state('');
  let toastTimer: ReturnType<typeof setTimeout>;
  let dialog: HTMLDialogElement;

  function announce(text: string) {
    clearTimeout(toastTimer);
    notice = text;
    toastTimer = setTimeout(() => notice = '', 4500);
  }
  function openLetter() { letterOpen = true; dialog.showModal(); }
  function closeLetter() { dialog.close(); letterOpen = false; }
  async function copyLetter() {
    try { await navigator.clipboard.writeText(current.letter); announce('요구서를 복사했습니다. 공식 창구에 붙여 넣어 주세요.'); }
    catch { announce('자동 복사가 지원되지 않습니다. 요구서 내용을 선택해 복사해 주세요.'); }
  }
  async function savePoster() {
    if (exporting) return;
    exporting = true;
    try { await downloadPoster(selected); announce('공유 포스터를 저장했습니다.'); }
    catch { announce('이미지를 저장하지 못했습니다. 다시 시도해 주세요.'); }
    finally { exporting = false; }
  }
  async function shareCampaign(topic: 'facts' | 'demand' = 'demand') {
    const data = {
      title: '병무청 신검, 내 기록도 연구에 쓰일까?',
      text: topic === 'facts'
        ? '병무청이 2015~2024년 신검 데이터를 연구에 제공한다는 사실, 알고 있었나요? 어떤 정보가 쓰이는지 함께 확인해 보세요.'
        : '병무청 신검에서 낸 ' + current.lines.join(' ') + ' — Oh My Health Data',
      url: absoluteUrl(topic === 'facts' ? '/#check' : '/#action')
    };
    try {
      if (navigator.share) await navigator.share(data);
      else { await navigator.clipboard.writeText(data.url); announce('캠페인 링크를 복사했습니다.'); }
    } catch (error) { if (!(error instanceof DOMException && error.name === 'AbortError')) announce('공유가 지원되지 않습니다. 주소창의 링크를 복사해 주세요.'); }
  }
  onMount(() => () => clearTimeout(toastTimer));
</script>

<Seo page={SEO_PAGES.home} />

<main id="main">
  <section class="hero container" aria-labelledby="hero-title">
    <div class="hero-copy">
      <h1 id="hero-title" class="personal-headline">병무청 신검,<br />내 기록도<br /><span class="highlight">연구에 쓰일까?</span></h1>
      <p class="hero-description">병무청은 <strong>2015~2024년 신검 데이터</strong>를<br class="desktop-break" /> 가명처리해 의료 연구에 제공합니다.<br /><strong>혈당·혈압·간염 검사까지.</strong> 어떤 정보가 쓰이는지 확인하세요.</p>
      <div class="hero-actions"><a class="button button-dark" href="#check">내 신검 연도 확인하기 <span aria-hidden="true">↓</span></a><a href="#story" class="text-link">어떤 정보가 쓰이나요? <span aria-hidden="true">↗</span></a></div>
      <a class="hero-footnote" href="/sources/#research"><span class="small-cross">+</span> 병무청이 공개한 연구 제공 내역에서 확인했습니다. ↗</a>
    </div>
    <HeroArtwork />
  </section>

  <div class="statement-strip" aria-hidden="true"><span>MY BODY.</span><Mark size={30} /><span>MY DATA.</span><Mark size={30} /><span>MY SAY.</span><Mark size={30} /><span>MY BODY.</span><Mark size={30} /><span>MY DATA.</span><Mark size={30} /><span>MY SAY.</span></div>

  <YearCheck />

  <section id="story" class="story-section section-pad">
    <div class="container">
      <div class="section-intro"><p class="eyebrow"><span class="section-number">01</span> 신검 그 이후</p></div>
      <div class="section-heading"><h2>신검 때 냈던 정보.<br /><span class="underlined">지금은 연구 자료입니다.</span></h2><p>피 뽑고, 시력 재고, 엑스레이 찍던 그날.<br />병무청은 그 검사 정보를 이렇게 활용합니다.</p></div>
      <div class="fact-grid">
        <article class="fact-panel fact-research">
          <div class="fact-top"><span class="tag">의학 연구</span><span class="fact-index">01 / 03</span></div>
          <div class="fact-visual word-stack" aria-hidden="true"><span>혈당 <small>GLUCOSE</small></span><span>혈압 <small>BLOOD PRESSURE</small></span><span>간염 <small>HEPATITIS</small></span><span class="word-more">+</span></div>
          <h3>키와 몸무게,<br />그 이상의 정보.</h3><p><strong>병무청 처리방침에 명시된<br />검사결과 45개 컬럼.</strong><br />2015~2024년 검사 데이터가<br />다른 기관의 의료데이터와 결합하는<br />연구에 제공됩니다.</p><a href="/sources/#research" class="source-link">병무청 제공 내역 보기 <span>↗</span></a>
        </article>
        <article class="fact-panel fact-ai">
          <div class="fact-top"><span class="tag">AI 학습</span><span class="fact-index">02 / 03</span></div>
          <div class="fact-visual image-count"><span class="count-plus" aria-hidden="true">+</span><strong>1,014<span>장</span></strong><span class="image-count-label">평발 진단 의료영상</span></div>
          <h3>검사를 위해 찍은 영상이<br />AI 학습 자료로.</h3><p>507명의 평발 진단 영상 1,014장.<br />가명처리된 의료영상이<br />데이터안심구역에서 연구에 쓰입니다.</p><a href="/sources/#research" class="source-link">공식 데이터 설명 보기 <span>↗</span></a>
        </article>
        <article class="fact-panel fact-retention">
          <div class="fact-top"><span class="tag">정보 보관</span><span class="fact-index">03 / 03</span></div>
          <div class="fact-visual forever"><span>보유기간</span><strong>영구<span class="stamp-dot">.</span></strong><div class="forever-rule"></div></div>
          <h3>기록에 적힌 두 글자.<br />‘영구’.</h3><p>서울·대전충남·전북지방병무청의<br />‘병역판정검사 수검자 파일’은<br />영구 보유로 등록되어 있습니다.</p><a href="/sources/#retention" class="source-link">개인정보파일 등록 보기 <span>↗</span></a>
        </article>
      </div>
      <p class="story-note">내가 낸 건강정보. 어디에 쓰이고 언제 지워지는지, 나도 알아야 합니다.</p>
    </div>
  </section>

  <section class="consent-section section-pad" aria-labelledby="consent-title">
    <div class="container consent-grid">
      <div><p class="eyebrow"><span class="section-number">02</span> 신검은 받았는데, 연구 동의는?</p><h2 id="consent-title">피는 내가 뽑았는데,<br /><span>선택은 누가 하나요?</span></h2><p class="consent-description">현행법은 과학적 연구 등을 위한 가명정보 처리를<br class="desktop-break" /> <strong>개별 동의 없이</strong> 허용합니다.</p><p class="consent-appeal">병역판정을 위해 의무적으로 낸 건강정보.<br />연구에 쓰이는 과정에는 내 선택도 있어야 합니다.</p><a href="/sources/#consent" class="source-link light-source">개인정보 보호법 제28조의2 <span>↗</span></a></div>
      <div class="consent-art" aria-hidden="true"><div class="consent-art-label">WHO GETS TO DECIDE?</div><div class="consent-question">?</div><div class="consent-art-bottom"><span>MY BODY<br />MY DATA</span><span class="outline-arrow">↗</span></div><div class="consent-tape">선택권을 보장하라.</div></div>
    </div>
  </section>

  <section id="action" class="action-section section-pad" aria-labelledby="action-title">
    <div class="container">
      <div class="section-intro"><p class="eyebrow"><span class="section-number">03</span> 이제, 우리의 목소리</p></div>
      <div class="section-heading action-heading"><h2 id="action-title">병무청에 묻겠습니다.<br /><span class="highlight">내 정보, 어떻게 썼습니까?</span></h2><p>공개·삭제 기준·선택권.<br />내가 가장 먼저 답받고 싶은 것을 고르세요.</p></div>
      <div class="action-grid">
        <div class="demand-controls">
          <fieldset><legend class="sr-only">가장 강조할 요구 선택</legend>
          {#each demands as demand}
            <label class:selected={selected === demand.id} class="demand-option">
              <input type="radio" name="demand" value={demand.id} bind:group={selected} />
              <span class="demand-number">{demand.number}</span><span class="demand-text"><strong>{demand.title}</strong><span>{demand.description}</span></span><span class="demand-check" aria-hidden="true">{selected === demand.id ? '↗' : '+'}</span>
            </label>
          {/each}
          </fieldset>
          <p class="choice-hint">선택하면 오른쪽 포스터가 바뀝니다. <span aria-hidden="true">↗</span></p>
        </div>
        <div class="poster-workspace">
          <div class="poster-preview" data-theme={selected} aria-live="polite" aria-label="선택한 요구 포스터">
            <div class="poster-top"><span>OH MY<br />HEALTH DATA.</span><Mark size={32} /></div>
            <span class="poster-label">이것이 나의 요구입니다.</span>
            {#key selected}<h3 class="poster-message">{#each current.lines as line}<span>{line}</span>{/each}</h3>{/key}
            <div class="poster-bottom"><span>병무청 건강정보 캠페인</span><span>MY DATA.<br />MY SAY.</span></div>
          </div>
          <div class="poster-tools"><button onclick={savePoster} disabled={exporting}><span aria-hidden="true">↓</span> {exporting ? '저장하는 중' : '포스터 저장'}</button><button onclick={() => shareCampaign()}><span aria-hidden="true">↗</span> 내 요구 공유</button></div>
        </div>
      </div>
      <div class="action-bar"><div><h3>병무청에 직접 요구하세요.</h3><p>선택한 요구에 맞는 청구 문안을 준비했습니다.</p></div><button class="button button-dark" onclick={openLetter}>내 요구서 만들기 <span aria-hidden="true">↗</span></button></div>
      <p class="agent-entry">에이전트를 사용하고 있나요? <a href="#agent-skill">민원 skill로 준비하기 ↗</a></p>
    </div>
  </section>

  <SkillPromo />

  <section class="spread-section" aria-labelledby="spread-title"><div class="container spread-inner"><div><p class="eyebrow">신검 받은 친구에게도</p><h2 id="spread-title">같이 신검 받은 친구는,<br />이 사실을 알고 있을까요?</h2><p>어떤 건강정보가 쓰이는지, 우리도 알아야 합니다.</p></div><button class="button button-dark" onclick={() => shareCampaign('facts')}>신검 받은 친구에게 알리기 <span aria-hidden="true">↗</span></button></div></section>

  <section class="evidence-banner"><div class="container"><div><h2>근거도, 함께 엽니다.</h2><p>병무청의 처리방침부터 데이터 목록과 법령까지.<br />이 캠페인의 주장을 뒷받침하는 공식 자료를 확인하세요.</p></div><a href="/sources/" class="evidence-arrow" aria-label="공식 근거 페이지로 이동">↗</a></div></section>
</main>

<dialog bind:this={dialog} onclose={() => letterOpen = false} class="letter-dialog" aria-labelledby="letter-title">
  {#if letterOpen}
    <div class="dialog-header"><span class="eyebrow">YOUR VOICE, IN WRITING</span><button onclick={closeLetter} aria-label="요구서 닫기" class="dialog-close">×</button></div>
    <h2 id="letter-title">나의 요구서</h2><p class="dialog-description">내용을 복사한 뒤 {current.route}에서 본인인증하고 제출하세요.</p>
    <label class="sr-only" for="letter-content">선택한 요구의 청구 문안</label><textarea id="letter-content" readonly value={current.letter}></textarea>
    <div class="dialog-actions"><button onclick={copyLetter} class="button button-dark">문안 복사 <span>＋</span></button><a href={current.url} target="_blank" rel="noopener noreferrer" class="button button-outline">{current.route} 열기 <span>↗</span></a></div>
    <p class="dialog-feedback" role="status">{notice}</p>
    <p class="dialog-note">이 페이지에서 개인정보를 수집하거나 민원을 자동 제출하지 않습니다.</p>
  {/if}
</dialog>
<div class="toast" class:visible={notice !== ''} role="status">{notice}</div>
