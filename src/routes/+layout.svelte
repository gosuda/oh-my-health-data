<script lang="ts">
  import '@fontsource-variable/noto-sans-kr';
  import '@fontsource/barlow-condensed/latin-700.css';
  import '@fontsource/barlow-condensed/latin-800.css';
  import '../app.css';
  import Mark from '$lib/Mark.svelte';

  let { children } = $props();
</script>

<a class="skip-link" href="#main">본문으로 바로가기</a>
<header class="site-header">
  <div class="header-inner">
    <a href="/" class="brand" aria-label="Oh My Health Data 홈">
      <Mark />
      <span>OH MY<br />HEALTH DATA<span class="brand-dot">.</span></span>
    </a>
    <nav aria-label="메인 메뉴">
      <a href="/#story" class="nav-story">신검 정보의 쓰임</a>
      <a href="/sources/">공식 근거 <span aria-hidden="true">↗</span></a>
      <a href="/#check" class="nav-action">내 신검 확인 <span aria-hidden="true">↗</span></a>
    </nav>
  </div>
</header>

{@render children()}

<footer class="site-footer">
  <div class="container footer-top">
    <a href="/" class="brand" aria-label="Oh My Health Data 홈"><Mark /><span>OH MY<br />HEALTH DATA.</span></a>
    <p>내 몸의 정보.<br /><strong>내 선택도 있어야 한다.</strong></p>
    <div class="footer-links">
      <a href="/sources/">공식 자료 보기 ↗</a>
      <a href="/#action">나의 요구 만들기 ↗</a>
      <a href="/#agent-skill">민원 skill 받기 ↗</a>
      <a class="repo-button" href="https://github.com/gosuda/oh-my-health-data" target="_blank" rel="noopener noreferrer"><img src="/github-mark.svg" alt="" width="21" height="21" /><span>웹 사이트 소스코드와 자료 공개</span><span aria-hidden="true">↗</span></a>
    </div>
  </div>
  <div class="container footer-bottom"><span>자유 오픈소스 소프트웨어 커뮤니티 <strong>gosuda</strong>에서 제작한 시민 캠페인</span><a class="footer-repo-url" href="https://github.com/gosuda/oh-my-health-data" target="_blank" rel="noopener noreferrer">github.com/gosuda/oh-my-health-data ↗</a></div>
</footer>
