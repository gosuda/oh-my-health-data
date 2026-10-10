<script>
  import Seo from '$lib/Seo.svelte';
  import { SEO_PAGES } from '$lib/seo';

  const sections = [
    { id: 'research', number: '01', label: '연구에 쓰이는 정보' },
    { id: 'consent', number: '02', label: '동의와 선택권' },
    { id: 'retention', number: '03', label: '보관과 삭제' },
    { id: 'psychiatry', number: '04', label: '정신건강 자료' }
  ];

  const offices = [
    { name: '서울지방병무청', id: 'PIF_000000000429577' },
    { name: '대전충남지방병무청', id: 'PIF_000000000429298' },
    { name: '전북지방병무청', id: 'PIF_000000000429808' }
  ];

  const psychiatryFields = [
    '연번', '부령코드', '부령조항', '질병명', '연령대', '시도',
    '3급', '4급', '5급', '6급', '7급'
  ];
</script>

<Seo page={SEO_PAGES.sources} />

<main id="main" class="source-page">
  <div class="page-intro">
    <a class="back-link" href="/">← 캠페인으로 돌아가기</a>
    <h1>우리의 요구에는<br /><span>근거가 있습니다.</span></h1>
    <div class="intro-bottom">
      <p class="intro-copy">
        병무청이 공개한 문서와 법령에서 확인했습니다.<br class="desktop-break" />
        어떤 정보인지, 어디까지 확인했는지 함께 적었습니다.
      </p>
      <p class="checked-date">마지막 확인 <time datetime="2026-10-09">2026. 10. 09.</time></p>
    </div>
  </div>

  <nav class="section-nav" aria-label="근거 목차">
    {#each sections as section}
      <a href={'#' + section.id}>
        <span class="nav-number">{section.number}</span>
        <span>{section.label}</span>
        <span class="nav-arrow" aria-hidden="true">↓</span>
      </a>
    {/each}
  </nav>

  <section id="research" class="evidence-section" aria-labelledby="research-title">
    <div class="source-section-heading">
      <p class="source-section-number">01 / 연구 활용</p>
      <h2 id="research-title">건강정보가<br /> 연구와 AI에<br /> 쓰입니다.</h2>
    </div>
    <div class="section-content">
      <p class="section-lead">
        병무청 개인정보 처리방침 제12항은 외부 기관의 연구 목적과 제공 항목을 공개합니다.
      </p>
      <a class="official-link" href="https://www.mma.go.kr/contents.do?mc=usr0000283" target="_blank" rel="noopener noreferrer">
        병무청 개인정보 처리방침 · 2026. 8. 20. 적용 <span aria-hidden="true">↗</span>
      </a>

      <article class="fact-block featured-fact">
        <p class="fact-label">평발 진단 의료영상 · AI 학습 모델 생성</p>
        <p class="large-fact">1,014<span>장</span></p>
        <p>
          507명의 평발 진단 영상입니다. 2022년 1월부터 2024년 6월까지의 자료에서
          추출했으며, 한국데이터산업진흥원 데이터안심구역 등에 이용 조건을 두고 제공합니다.
          공개 설명에는 이름·병적번호 대체와 폐쇄 분석환경이 명시돼 있습니다.
        </p>
        <a class="official-link" href="https://www.data.go.kr/data/15146899/fileData.do" target="_blank" rel="noopener noreferrer">
          공공데이터포털 · 평발 측정 의료영상 설명 <span aria-hidden="true">↗</span>
        </a>
      </article>

      <article class="fact-block">
        <p class="fact-label">2015–2024년 병역판정검사 · 의료데이터 결합 연구</p>
        <h3>검사 결과를 다른 의료데이터와 결합하는 연구.</h3>
        <p>
          처리방침은 한국보건의료정보원의 보건의료 빅데이터 플랫폼에 기본항목
          2,820,977행과 검사결과 2,745,820행을 제공한다고 밝힙니다.
          두 표의 행 수를 합산해 사람 수로 표현할 수는 없습니다.
          현재 카탈로그에는 혈액·소변·간염 등의 검사값이 나옵니다.
        </p>
        <div class="official-links">
          <a class="official-link" href="https://hcdl.mohw.go.kr/catalog/detail/Y/MMA_BASE/H0014" target="_blank" rel="noopener noreferrer">
            HCDL · 신체검사 기본정보 <span aria-hidden="true">↗</span>
          </a>
          <a class="official-link" href="https://hcdl.mohw.go.kr/catalog/detail/Y/MMA_BYPJ/H0014" target="_blank" rel="noopener noreferrer">
            HCDL · 병역판정검사 결과 <span aria-hidden="true">↗</span>
          </a>
        </div>
        <p class="scope-note">
          항목 수는 처리방침의 <strong>8+45열</strong>, 2025년 보건복지부 발표의
          <strong>55항목</strong>, 현재 카탈로그의 <strong>8+48열</strong>로 서로 다릅니다.
          산정 기준과 변경 이력은 추가 확인이 필요합니다. 현재 명세를 2025년 제공 당시와
          동일하다고 단정하지 않으며, 두 표에는 공통 항목도 있습니다.
          <a href="https://www.mohw.go.kr/board.es?mid=a10503010100&bid=0027&act=view&list_no=1487314" target="_blank" rel="noopener noreferrer">보건복지부 발표 원문 ↗</a>
        </p>
      </article>

      <article class="fact-block compact-fact">
        <h3>군 장병 의료이용 분석에도 사용합니다.</h3>
        <p>
          같은 처리방침에는 국군의무사령부의 의료이용 행태 분석을 위한
          출생연도·나이·신장·체중 제공도 기재돼 있습니다.
          세 연구의 공개 처리기간은 2026년 12월 31일까지입니다.
          이는 원본이나 학습 모델을 모두 삭제하는 날짜를 뜻하지 않습니다.
        </p>
      </article>
    </div>
  </section>

  <section id="consent" class="evidence-section" aria-labelledby="consent-title">
    <div class="source-section-heading">
      <p class="source-section-number">02 / 동의와 선택권</p>
      <h2 id="consent-title">동의를 받지<br /> 않아도 되는<br /> 예외가 있습니다.</h2>
    </div>
    <div class="section-content">
      <p class="section-lead">
        개인정보 보호법 제28조의2는 통계작성·과학적 연구·공익적 기록보존 등을 위해
        동의 없이 가명정보를 처리할 수 있도록 합니다.
      </p>
      <p>
        가명정보는 추가 정보 없이는 특정 개인을 알아볼 수 없도록 처리한 정보입니다.
        법은 제3자 제공 시 식별정보 제한, 안전조치, 재식별 금지 의무도 두고 있습니다.
        개별 연구가 이 요건을 모두 충족했는지는 별도로 확인해야 합니다.
      </p>
      <a class="official-link" href="https://law.go.kr/LSW/lsLinkCommonInfo.do?lsJoLnkSeq=1020398635" target="_blank" rel="noopener noreferrer">
        개인정보 보호법 제28조의2–5 <span aria-hidden="true">↗</span>
      </a>

      <article class="fact-block">
        <h3>일반적인 삭제·처리정지 요구에도 제한이 있습니다.</h3>
        <p>
          제28조의7은 해당 특례에 따라 처리된 가명정보에 열람·정정 및 삭제·처리정지 등의
          권리를 적용하지 않습니다. 원본 개인정보에 대한 권리와 위법한 처리에 대한
          문제 제기까지 사라지는 것은 아닙니다.
        </p>
        <a class="official-link" href="https://law.go.kr/lsLinkCommonInfo.do?lsJoLnkSeq=1020398611" target="_blank" rel="noopener noreferrer">
          개인정보 보호법 제28조의7 <span aria-hidden="true">↗</span>
        </a>
      </article>
      <p class="demand-note">그래서 우리는 연구 활용에<br /><strong>선택권을 보장하라고 요구합니다.</strong></p>
      <p class="small-note">위 법령은 2026년 9월 11일 시행본을 확인했습니다.</p>
    </div>
  </section>

  <section id="retention" class="evidence-section" aria-labelledby="retention-title">
    <div class="source-section-heading">
      <p class="source-section-number">03 / 보관과 삭제</p>
      <h2 id="retention-title">어떤 자료는 1년.<br /> 어떤 파일은<br /> <span class="source-highlight">영구.</span></h2>
    </div>
    <div class="section-content">
      <p class="section-lead">자료 종류에 따라 공개된 보유기간이 다릅니다.</p>
      <div class="retention-table-wrap">
        <table>
          <caption>공개 등록과 현행 규정에서 확인한 보유기간</caption>
          <thead>
            <tr><th scope="col">자료</th><th scope="col">기간</th></tr>
          </thead>
          <tbody>
            <tr>
              <td>서울·대전충남·전북의<br /><strong>병역판정검사 수검자 파일</strong></td>
              <td class="period permanent">영구</td>
            </tr>
            <tr><td>정상자의 흉부촬영 영상</td><td class="period">1년</td></tr>
            <tr><td>그 밖의 자체·외부 의료영상</td><td class="period">10년</td></tr>
            <tr><td>병무용진단서 등 질병 관련 자료와<br />이미지 등록이 곤란한 자료의 묶음</td><td class="period">10년</td></tr>
          </tbody>
        </table>
      </div>
      <p class="scope-note">
        ‘영구’는 위 세 지방청의 공개등록에서 확인한 <strong>수검자 파일</strong>의 기간입니다.
        등록 갱신일은 표시되지 않습니다. 모든 검사수치·영상·스캔본이 영구 보관된다는
        뜻으로 넓혀 해석하지 않습니다.
      </p>
      <div class="official-links office-links">
        {#each offices as office}
          <a class="official-link" href={'https://www.privacy.go.kr/wcp/pif/sch/personalInfoFileViewPopup.do?prsnInfoFileId=' + office.id} target="_blank" rel="noopener noreferrer">
            {office.name} 등록정보 <span aria-hidden="true">↗</span>
          </a>
        {/each}
      </div>

      <article class="fact-block">
        <h3>규정과 실제 삭제 사이를 확인해야 합니다.</h3>
        <p>
          병역판정검사 규정 제23조 제10항은 영상의 보관기간이 지난 후 다음연도
          1월 30일까지 공공기록물법에 따른 폐기를 규정합니다. 제55조는 판정자료의
          스캔 등록과 질병 관련 자료 묶음의 10년 보관을 정합니다.
          스캔본·백업·별도 사본에 적용되는 기준과 실제 삭제 이행은 추가 확인이 필요합니다.
        </p>
        <a class="official-link" href="https://www.law.go.kr/admRulInfoP.do?admRulSeq=2100000272256" target="_blank" rel="noopener noreferrer">
          병역판정검사 규정 제23조·제55조 · 2026. 1. 8. 시행 <span aria-hidden="true">↗</span>
        </a>
        <p class="scope-note">
          국가기록원이 2022년 1월 발간한 사례집에는 병무청 의료영상 시스템의
          10년 보존과 20년 처분 제약을 합친 운영 사례도 있습니다.
          이는 과거 특정 사례이며, 현재 모든 영상의 보유기간을 30년으로 설명하는 근거는 아닙니다.
          <a href="https://www.archives.go.kr/next/common/downloadBoardFile.do?board_file_seq=2&board_seq=101576" target="_blank" rel="noopener noreferrer">국가기록원 사례집 · 69–74쪽 ↗</a>
        </p>
      </article>
    </div>
  </section>

  <section id="psychiatry" class="evidence-section" aria-labelledby="psychiatry-title">
    <div class="source-section-heading">
      <p class="source-section-number">04 / 정신건강 자료</p>
      <h2 id="psychiatry-title">공개 명세에는<br /> <span class="source-highlight">‘질병명’</span>도<br /> 있습니다.</h2>
    </div>
    <div class="section-content">
      <p class="fact-label">K-data · 정신건강의학과 부령별 처분현황 · MMA_016</p>
      <p class="section-lead">
        병무청이 제공기관으로 등록된 이 자료의 명세에는 질병명을 포함한 11개 항목이 있습니다.
      </p>
      <p>
        2025년 6월 26일 등록된 설명은 2023년 정신질환별 병역처분 현황 15,994건과
        합동 데이터분석·아이디어 공모전 활용 목적을 밝힙니다.
        앞서 소개한 HCDL 검사결과와는 별도 데이터셋입니다.
      </p>
      <ul class="field-list" aria-label="공개 명세의 11개 항목">
        {#each psychiatryFields as field}
          <li class:emphasized={field === '질병명'}>{field}</li>
        {/each}
      </ul>
      <a class="official-link" href="https://dsz.kdata.or.kr/member/apply/add/data_detail.do?dataId=MMA_016" target="_blank" rel="noopener noreferrer">
        K-data 데이터안심구역 · 해당 자료 설명 <span aria-hidden="true">↗</span>
      </a>
      <p class="scope-note">
        이 명세만으로 개인 단위인지 집계 단위인지, 실제 어느 연구자가 이용했는지는
        확인할 수 없습니다. 병원 진료기록 원문이 제공됐다는 증거도 아닙니다.
        질병명 항목의 존재와 개인별 진료기록 제공 여부를 구분합니다.
      </p>
      <article class="fact-block">
        <h3>외부에서 취득한 자료에는 별도 목적 제한이 있습니다.</h3>
        <p>
          병역법 제11조의2는 같은 조에 따라 취득한 진료기록 등의 정보·자료를
          병역판정검사 외 목적으로 사용하는 것을 금지합니다.
          이 정보가 연구 데이터 생성에 쓰였는지와 법적 적용 관계는 기관에 확인해야 합니다.
        </p>
        <a class="official-link" href="https://www.law.go.kr/lsLawLinkInfo.do?chrClsCd=010202&lsJoLnkSeq=1000459255" target="_blank" rel="noopener noreferrer">
          병역법 제11조의2 · 2026. 10. 2. 시행 <span aria-hidden="true">↗</span>
        </a>
      </article>
    </div>
  </section>

  <div class="closing-action">
    <p>누구에게 무엇을 제공했는지.<br />언제, 무슨 기준으로 삭제하는지.<br /><strong>병무청은 답하십시오.</strong></p>
    <a href="/">캠페인으로 돌아가기 <span aria-hidden="true">↗</span></a>
  </div>
</main>

<style>
  .source-page {
    --paper: #f2f0e7;
    --ink: #171916;
    --acid: #e5ff36;
    color: var(--ink);
    background: var(--paper);
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 clamp(20px, 4vw, 56px) 80px;
    word-break: keep-all;
    overflow-wrap: anywhere;
  }

  .source-page a { color: inherit; }
  .source-page a:focus-visible { outline: 3px solid var(--ink); outline-offset: 5px; }
  .page-intro { padding: 32px 0 36px; }
  .back-link { font-size: 13px; font-weight: 700; text-decoration: none; }
  .back-link:hover { text-decoration: underline; text-underline-offset: 4px; }
  h1, h2, h3, p { margin: 0; }
  h1 { margin-top: 44px; font-size: clamp(38px, 6.8vw, 80px); font-weight: 900; line-height: 1.13; letter-spacing: -.065em; }
  h1 span { text-decoration: underline; text-decoration-color: var(--acid); text-decoration-thickness: .13em; text-underline-offset: .03em; text-decoration-skip-ink: none; }
  .intro-bottom { display: flex; align-items: end; justify-content: space-between; gap: 24px; margin-top: 32px; }
  .intro-copy { font-size: clamp(15px, 1.6vw, 18px); line-height: 1.8; }
  .checked-date { font-size: 12px; white-space: nowrap; line-height: 1.8; }
  .checked-date time { display: block; font-weight: 800; }

  .section-nav { display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); }
  .section-nav a { display: flex; align-items: center; gap: 10px; min-height: 70px; padding: 14px 18px; font-size: 13px; font-weight: 800; text-decoration: none; }
  .section-nav a + a { border-left: 1px solid var(--ink); }
  .section-nav a:hover { background: var(--acid); }
  .nav-number { font-size: 10px; font-variant-numeric: tabular-nums; }
  .nav-arrow { margin-left: auto; font-size: 19px; }

  .evidence-section { display: grid; grid-template-columns: .9fr 1.4fr; gap: clamp(32px, 6vw, 80px); padding: 72px 0; border-bottom: 1px solid var(--ink); scroll-margin-top: 100px; }
  .source-section-number { margin-bottom: 20px; font-size: 12px; font-weight: 800; letter-spacing: .04em; }
  h2 { font-size: clamp(30px, 3.5vw, 42px); line-height: 1.25; letter-spacing: -.055em; font-weight: 900; }
  .source-highlight { background: var(--acid); padding: 0 .06em; box-decoration-break: clone; }
  .section-content { min-width: 0; }
  .section-content p { font-size: 15px; line-height: 1.85; }
  .section-content .section-lead { font-size: 20px; line-height: 1.6; font-weight: 700; letter-spacing: -.025em; margin-bottom: 18px; }
  .official-link { display: inline-flex; align-items: baseline; gap: 8px; font-size: 12px; font-weight: 750; line-height: 1.8; margin-top: 16px; text-decoration-thickness: 1px; text-underline-offset: 4px; }
  .official-link:hover, .scope-note a:hover { text-decoration-thickness: 2px; }
  .official-link span { flex-shrink: 0; }
  .official-links { display: flex; flex-direction: column; align-items: start; gap: 4px; margin-top: 12px; }
  .official-links .official-link { margin-top: 0; }
  .fact-block { border-top: 1px solid rgba(23, 25, 22, .35); margin-top: 32px; padding-top: 28px; }
  .featured-fact { background: var(--acid); padding: 25px; border: 1px solid var(--ink); }
  .section-content .fact-label { font-size: 11px; font-weight: 800; letter-spacing: .015em; margin-bottom: 12px; }
  .section-content .large-fact { font-size: clamp(68px, 8vw, 102px); font-weight: 900; letter-spacing: -.07em; line-height: 1.05; margin-bottom: 22px; }
  .large-fact span { font-size: 25px; margin-left: 10px; letter-spacing: -.04em; }
  h3 { font-size: 20px; font-weight: 800; letter-spacing: -.035em; line-height: 1.5; margin-bottom: 12px; }
  .section-content .scope-note { border-left: 2px solid var(--ink); padding-left: 16px; font-size: 13px; line-height: 1.85; margin-top: 24px; }
  .scope-note a { display: inline; text-underline-offset: 3px; }
  .scope-note strong { font-weight: 750; }
  .section-content .demand-note { margin-top: 32px; background: var(--acid); padding: 20px 24px; font-size: 19px; line-height: 1.6; }
  .section-content .small-note { margin-top: 16px; font-size: 11px; }

  .retention-table-wrap { margin-top: 28px; }
  table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
  caption { text-align: left; font-size: 11px; margin-bottom: 14px; }
  th { border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); padding: 12px 0; font-size: 11px; }
  td { border-bottom: 1px solid rgba(23, 25, 22, .35); padding: 19px 0; line-height: 1.7; }
  td:first-child { padding-right: 18px; }
  .period { font-size: 23px; font-weight: 900; white-space: nowrap; width: 76px; }
  .permanent { background: var(--acid); text-align: center; }
  .office-links { margin-top: 20px; }
  .field-list { display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 24px 0 8px; list-style: none; }
  .field-list li { border: 1px solid var(--ink); padding: 7px 12px; font-size: 12px; }
  .field-list .emphasized { background: var(--acid); font-weight: 800; }
  .closing-action { display: flex; align-items: end; justify-content: space-between; gap: 32px; padding-top: 48px; }
  .closing-action p { font-size: clamp(21px, 2.5vw, 28px); line-height: 1.6; letter-spacing: -.035em; }
  .closing-action a { display: inline-flex; justify-content: space-between; gap: 32px; padding: 17px 23px; background: var(--ink); color: var(--paper); font-size: 13px; font-weight: 800; text-decoration: none; }
  .closing-action a:hover { background: var(--acid); color: var(--ink); }

  @media (max-width: 800px) {
    .section-nav { grid-template-columns: repeat(2, 1fr); }
    .section-nav a { min-height: 61px; }
    .section-nav a:nth-child(3) { border-left: 0; }
    .section-nav a:nth-child(n+3) { border-top: 1px solid var(--ink); }
    .evidence-section { grid-template-columns: 1fr; gap: 30px; padding: 48px 0; }
    .source-section-heading h2 br { display: none; }
    .source-section-heading h2 { max-width: 520px; }
    .source-section-number { margin-bottom: 16px; }
    .section-content { max-width: 650px; }
    .closing-action { align-items: start; flex-direction: column; }
  }

  @media (max-width: 480px) {
    .source-page { padding-bottom: 56px; }
    .page-intro { padding-top: 24px; }
    h1 { font-size: clamp(34px, 8.9vw, 43px); }
    .intro-bottom { align-items: start; flex-direction: column; gap: 20px; margin-top: 24px; }
    .checked-date time { display: inline; margin-left: 8px; }
    .desktop-break { display: none; }
    .section-nav a { padding: 12px; font-size: 12px; gap: 8px; }
    .section-content .section-lead { font-size: 18px; }
    .featured-fact { padding: 20px; }
    .section-content .demand-note { padding: 18px; font-size: 17px; }
    td { font-size: 12px; }
    .period { font-size: 21px; width: 61px; }
    .closing-action a { width: 100%; box-sizing: border-box; }
  }
</style>
