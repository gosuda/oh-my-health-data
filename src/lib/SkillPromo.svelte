<script lang="ts">
  const request = 'mma-health-data skill을 사용해 병무청에 어떤 건강정보를 연구용으로 제공했고, 얼마나 보관하며, 삭제나 연구 활용 제외를 요청할 수 있는지 묻는 청구서를 준비해 줘.';
  let feedback = $state('');

  async function copyRequest() {
    try {
      await navigator.clipboard.writeText(request);
      feedback = '요청을 복사했습니다. skill을 추가한 에이전트에 붙여 넣어 주세요.';
    } catch {
      feedback = '아래 요청 문장을 선택해 복사해 주세요.';
    }
  }
</script>

<section id="agent-skill" class="skill-promo" aria-labelledby="skill-title">
  <div class="container skill-grid">
    <div class="skill-copy">
      <h2 id="skill-title">민원 문안,<br /><span>에이전트에게 맡기세요.</span></h2>
      <p class="skill-description">어떤 정보를 줬는지, 언제 지우는지, 연구에서 빠질 수 있는지.<br />묻고 싶은 내용을 말하면 에이전트가 청구서를 준비합니다.</p>
      <ul class="skill-features"><li>내 질문에 맞는 청구·민원 유형 선택</li><li>공식 근거와 템플릿으로 문안 자동 작성</li><li>받은 답변 분석과 후속 질문 정리</li></ul>
      <div class="skill-actions"><a class="button skill-download" href="/downloads/mma-health-data.zip" download>민원 skill 받기 <span aria-hidden="true">↓</span></a><a class="skill-source" href="https://github.com/gosuda/ohy-my-health-data/tree/main/skills/mma-health-data" target="_blank" rel="noopener noreferrer">skill 소스 보기 ↗</a></div>
    </div>
    <div class="skill-start">
      <ol class="skill-steps"><li><span>01</span>ZIP을 받고 압축을 풀어 주세요.</li><li><span>02</span>폴더 전체를 사용하는 에이전트에 skill로 추가하세요.</li><li><span>03</span>아래 문장으로 민원 준비를 요청하세요.</li></ol>
      <div class="skill-prompt"><p>{request}</p><button onclick={copyRequest}>사용 요청 복사 <span aria-hidden="true">＋</span></button></div>
      <p class="skill-feedback" role="status">{feedback}</p>
      <details class="skill-details"><summary>공식 창구 접수는 어떻게 하나요?</summary><p>브라우저 도구가 있는 에이전트는 공식 포털의 입력과 접수 확인 절차도 도울 수 있습니다. 본인인증과 제출할 내용 확인은 직접 진행합니다.</p><p>브라우저 도구가 없으면 작성한 문안을 공식 창구에 붙여 넣어 제출할 수 있습니다.</p></details>
    </div>
  </div>
</section>

<style>
  .skill-promo { background: var(--ink); color: var(--paper); padding-block: 72px; scroll-margin-top: 20px; }
  .skill-grid { display: grid; grid-template-columns: 1.05fr 1fr; gap: 65px; align-items: start; }
  h2 { font-size: clamp(30px, 3.5vw, 48px); font-weight: 850; line-height: 1.35; letter-spacing: -.065em; }
  h2 span { color: var(--acid); }
  .skill-description { font-size: 14px; line-height: 1.9; color: #d2d5c9; margin-top: 24px; }
  .skill-features { padding: 0; margin: 24px 0 0; list-style: none; display: grid; gap: 10px; font-size: 12px; line-height: 1.8; }
  .skill-features li::before { content: '+'; color: var(--acid); margin-right: 12px; font-weight: 800; }
  .skill-actions { display: flex; align-items: center; flex-wrap: wrap; gap: 22px; margin-top: 29px; }
  .skill-download { background: var(--acid); color: var(--ink); border-color: var(--acid); }
  .skill-download:hover { background: var(--paper); border-color: var(--paper); }
  .skill-source { font-size: 11px; border-bottom: 1px solid #79836c; padding-block: 6px; }
  .skill-start { padding: 28px; border: 1px solid #657058; }
  .skill-steps { list-style: none; margin: 0; padding: 0; display: grid; gap: 16px; font-size: 12px; line-height: 1.8; }
  .skill-steps li { display: flex; gap: 13px; align-items: baseline; word-break: keep-all; }
  .skill-steps span { color: var(--acid); font-family: var(--display); font-size: 19px; flex-shrink: 0; }
  .skill-prompt { margin-top: 25px; padding: 20px; background: #293124; border: 1px solid #58634b; }
  .skill-prompt p { font-size: 13px; line-height: 1.9; user-select: text; }
  .skill-prompt button { display: flex; align-items: center; justify-content: space-between; width: 100%; margin-top: 18px; padding: 11px 0 0; border: 0; border-top: 1px solid #647453; background: transparent; color: var(--acid); font-size: 12px; font-weight: 700; }
  .skill-prompt button:hover { color: white; }
  .skill-feedback { min-height: 1.8em; margin-top: 10px; font-size: 10px; line-height: 1.8; color: var(--acid); }
  .skill-details { margin-top: 12px; border-top: 1px solid #57634a; padding-top: 17px; }
  .skill-details summary { cursor: pointer; font-size: 12px; font-weight: 600; line-height: 1.8; }
  .skill-details p { margin-top: 12px; font-size: 11px; line-height: 1.9; color: #c0c8b5; }
  @media (max-width: 950px) {
    .skill-grid { grid-template-columns: 1fr; gap: 34px; }
    .skill-description br { display: none; }
  }
  @media (max-width: 560px) {
    .skill-promo { padding-block: 48px; }
    h2 { font-size: clamp(27px, 7vw, 37px); }
    .skill-description { font-size: 12px; margin-top: 20px; }
    .skill-features { font-size: 11px; }
    .skill-actions { gap: 17px; }
    .skill-download { width: 100%; font-size: 13px; }
    .skill-start { padding: 20px; }
    .skill-steps { font-size: 11px; }
    .skill-prompt { padding: 16px; }
    .skill-prompt p { font-size: 12px; }
    .skill-details summary { font-size: 11px; }
  }
</style>
