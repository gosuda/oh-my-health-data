# GitHub Pages 배포

`https://oh-my-health-data.com`에 정적 사이트를 배포합니다. [배포 워크플로](../.github/workflows/pages.yml)는 `gosuda` 소유의 공개 저장소에서 `main` 브랜치를 푸시하거나 수동 실행할 때 동작합니다.

## 최초 설정

운영 저장소는 [`gosuda/oh-my-health-data`](https://github.com/gosuda/oh-my-health-data)입니다. 저장소가 공개 상태이고 `main`에 배포 워크플로가 있어야 합니다.

1. gosuda 조직의 **Settings → Pages → Add a domain**에서 `oh-my-health-data.com`을 추가합니다. GitHub가 표시하는 TXT 레코드를 DNS에 등록하고 **Verify**를 누릅니다. 인증 후에도 TXT 레코드는 유지합니다.
2. 저장소의 **Settings → Pages → Build and deployment → Source**를 **GitHub Actions**로 선택합니다.
3. 같은 화면의 **Custom domain**에 `oh-my-health-data.com`을 입력하고 저장합니다. 이 설정을 먼저 저장한 다음 아래 DNS 레코드를 연결합니다.
4. DNS 서비스에서 다음 레코드를 설정합니다. `@`는 `oh-my-health-data.com`을 뜻합니다.

   | 유형 | 이름 | 값 |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | gosuda.github.io |

   위 레코드는 루트 도메인과 `www`에 적용합니다. 분석 서버 `q.oh-my-health-data.com`의 레코드는 별도로 유지합니다. 기존 `@`·`www`의 다른 호스팅용 A·AAAA·CNAME 레코드가 있다면 새 설정과 충돌하지 않도록 정리합니다.

   IPv6도 사용하려면 `@`의 AAAA 레코드에 `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`을 추가합니다.

5. **Actions → Deploy GitHub Pages → Run workflow → main**으로 첫 배포를 실행합니다. 이후에는 `main` 푸시마다 자동 배포됩니다.
6. Pages의 DNS 검사와 인증서 발급이 끝나면 **Enforce HTTPS**를 켭니다. DNS 반영과 HTTPS 옵션 활성화에는 최대 24시간이 걸릴 수 있습니다.

조직의 Actions 정책에서 공식 `actions/*` 사용이 허용되어 있어야 합니다. 배포 환경의 브랜치 제한을 설정한다면 **Settings → Environments → github-pages**에서 `main`을 허용합니다. 별도 PAT나 배포용 Secret은 필요하지 않습니다.

## 배포 내용과 확인

Node.js 24에서 `npm ci`, `npm run check`, `npm run build`를 실행하고 SEO·청구서·skill ZIP 테스트를 통과한 뒤 `build/`만 배포합니다. 원본 조사 문서나 개인 청구 파일을 별도로 업로드하지 않습니다.

커스텀 도메인의 루트에서 서비스하므로 SvelteKit의 `paths.base`에 저장소 이름을 넣지 않습니다. Actions 배포에서는 `CNAME` 파일 대신 Pages 설정의 Custom domain을 사용하며, `.nojekyll` 파일도 필요하지 않습니다.

배포 후 다음 항목을 확인합니다.

- `/`, `/sources/`, `/robots.txt`, `/sitemap.xml`, `/og/home.png`가 열리는지
- `/downloads/mma-health-data.zip`을 내려받아 압축을 풀 수 있는지
- 존재하지 않는 중첩 주소가 HTTP 404와 오류 페이지를 반환하는지
- HTTP 및 `www` 주소가 `https://oh-my-health-data.com`으로 이동하는지
- 사이트의 GitHub 링크가 운영 저장소를 여는지

## 공식 안내

- [GitHub Actions로 Pages 배포](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [조직의 커스텀 도메인 인증](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)
- [커스텀 도메인·DNS·HTTPS 설정](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
- [SvelteKit 정적 어댑터와 GitHub Pages](https://svelte.dev/docs/kit/adapter-static#GitHub-Pages)
