import { SITE_NAME, SITE_URL } from './site';

export type SeoPage = {
  path: '/' | '/sources/';
  title: string;
  description: string;
  image: string;
  imageAlt: string;
  type: 'WebPage' | 'CollectionPage';
  breadcrumb?: string;
};

export const SEO_PAGES = {
  home: {
    path: '/',
    title: `병무청 신검, 내 기록도 연구에 쓰일까? | ${SITE_NAME}`,
    description: '병무청 신검 건강정보의 연구 제공 항목과 보존기간, 동의·삭제 제도를 확인하세요. 2015~2024년 검사 연도 비교, 공식 근거, 민원 문안과 공개 에이전트 skill을 제공합니다.',
    image: '/og/home.png',
    imageAlt: '병무청 신검, 내 기록도 연구에 쓰일까? — Oh My Health Data 건강정보 캠페인',
    type: 'WebPage'
  },
  sources: {
    path: '/sources/',
    title: `병무청 건강정보 연구·보존기간 공식 근거 | ${SITE_NAME}`,
    description: '병무청 개인정보 처리방침, 연구 데이터 카탈로그, 개인정보 보호법에서 건강정보 제공 항목과 보존기간, 가명정보의 동의·삭제 제도를 확인하세요. gosuda 캠페인의 공식 출처 모음입니다.',
    image: '/og/sources.png',
    imageAlt: '병무청 건강정보 공식 근거 — 연구 제공 항목, 보존기간, 동의와 선택권에 관한 공식 자료',
    type: 'CollectionPage',
    breadcrumb: '공식 근거'
  }
} satisfies Record<string, SeoPage>;

export function absoluteUrl(path: string): string {
  return new URL(path, SITE_URL).href;
}

export function structuredData(page: SeoPage) {
  const canonical = absoluteUrl(page.path);
  const websiteId = absoluteUrl('/#website');
  const organizationId = absoluteUrl('/#organization');
  const imageId = `${canonical}#primaryimage`;
  const graph: Record<string, unknown>[] = [
    {
      '@type': 'Organization',
      '@id': organizationId,
      name: 'gosuda',
      description: '자유 오픈소스 소프트웨어 커뮤니티',
      url: 'https://github.com/gosuda'
    },
    {
      '@type': 'WebSite',
      '@id': websiteId,
      url: absoluteUrl('/'),
      name: SITE_NAME,
      inLanguage: 'ko-KR',
      publisher: { '@id': organizationId },
      image: {
        '@type': 'ImageObject',
        url: absoluteUrl('/logo.png'),
        width: 512,
        height: 512,
        caption: `${SITE_NAME} 캠페인 로고`
      }
    },
    {
      '@type': 'ImageObject',
      '@id': imageId,
      url: absoluteUrl(page.image),
      width: 1200,
      height: 630,
      caption: page.imageAlt
    },
    {
      '@type': page.type,
      '@id': `${canonical}#webpage`,
      url: canonical,
      name: page.title,
      description: page.description,
      inLanguage: 'ko-KR',
      isAccessibleForFree: true,
      isPartOf: { '@id': websiteId },
      publisher: { '@id': organizationId },
      primaryImageOfPage: { '@id': imageId },
      ...(page.breadcrumb ? { breadcrumb: { '@id': `${canonical}#breadcrumb` } } : {})
    }
  ];

  if (page.breadcrumb) {
    graph.push({
      '@type': 'BreadcrumbList',
      '@id': `${canonical}#breadcrumb`,
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: SITE_NAME, item: absoluteUrl('/') },
        { '@type': 'ListItem', position: 2, name: page.breadcrumb, item: canonical }
      ]
    });
  }

  return { '@context': 'https://schema.org', '@graph': graph };
}

export function serializeJsonLd(data: unknown): string {
  return JSON.stringify(data).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
}
