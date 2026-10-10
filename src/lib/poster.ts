export type PosterTheme = 'disclosure' | 'retention' | 'choice';

const posters: Record<PosterTheme, { number: string; headings: readonly string[] }> = {
	disclosure: {
		number: '01',
		headings: ['내 건강정보.', '어디에 썼는지', '공개하라.']
	},
	retention: {
		number: '02',
		headings: ['내 건강정보.', '언제 지우는지', '밝혀라.']
	},
	choice: {
		number: '03',
		headings: ['내 몸의 정보다.', '내 선택도', '있어야 한다.']
	}
};

const width = 1080;
const height = 1350;
const inset = 76;
const ink = '#171916';
const lime = '#e5ff36';
const cream = '#f2f0e7';
const fontFamily =
	'"Noto Sans KR Variable", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif';

function drawText(
	context: CanvasRenderingContext2D,
	text: string,
	x: number,
	y: number,
	size: number,
	weight: number,
	color: string,
	maxWidth = width - inset * 2
): void {
	let fittedSize = size;
	context.font = `${weight} ${fittedSize}px ${fontFamily}`;
	while (context.measureText(text).width > maxWidth && fittedSize > 20) {
		fittedSize -= 1;
		context.font = `${weight} ${fittedSize}px ${fontFamily}`;
	}
	context.fillStyle = color;
	context.fillText(text, x, y);
}

/** Creates a shareable campaign poster locally, without sending data anywhere. */
export async function downloadPoster(theme: PosterTheme): Promise<void> {
	if (typeof document === 'undefined' || typeof window === 'undefined') {
		throw new Error('포스터 다운로드는 브라우저에서 이용할 수 있습니다.');
	}

	const poster = posters[theme];
	if (!poster) {
		throw new Error('포스터 주제를 찾을 수 없습니다.');
	}

	// Load the poster weight as well as waiting for the page's existing font requests.
	// Either registered Noto family is supported; unavailable fonts use local fallbacks.
	if (document.fonts) {
		const text = [
			...poster.headings,
			poster.number,
			'우리는 요구합니다',
			'공개 · 보존 · 선택',
			'내 정보에 대한 결정권을 요구합니다.',
			'OH MY HEALTH DATA',
			'oh-my-health-data.com'
		].join('');
		await Promise.allSettled([
			document.fonts.load('900 124px "Noto Sans KR Variable"', text),
			document.fonts.load('900 124px "Noto Sans KR"', text)
		]);
		await document.fonts.ready;
	}

	const canvas = document.createElement('canvas');
	canvas.width = width;
	canvas.height = height;
	const context = canvas.getContext('2d');
	if (!context) {
		throw new Error('이 브라우저에서 포스터 이미지를 만들 수 없습니다.');
	}

	context.fillStyle = ink;
	context.fillRect(0, 0, width, height);
	context.textBaseline = 'alphabetic';
	context.textAlign = 'left';

	context.fillStyle = lime;
	context.fillRect(inset, 87, 54, 7);
	drawText(context, '우리는 요구합니다', 154, 103, 33, 700, cream);
	drawText(context, poster.number, 950, 103, 33, 700, lime, 54);

	context.fillStyle = cream;
	context.globalAlpha = 0.25;
	context.fillRect(inset, 157, width - inset * 2, 2);
	context.globalAlpha = 1;

	poster.headings.forEach((heading, index) => {
		drawText(context, heading, inset, 343 + index * 157, 124, 900, index === 2 ? lime : cream);
	});

	drawText(context, '공개 · 보존 · 선택', inset, 803, 28, 500, cream);
	context.fillStyle = lime;
	context.fillRect(0, 884, width, height - 884);
	drawText(context, '내 정보에 대한 결정권을 요구합니다.', inset, 990, 43, 900, ink);
	context.fillStyle = ink;
	context.fillRect(inset, 1043, width - inset * 2, 2);
	drawText(context, 'OH MY HEALTH DATA', inset, 1156, 55, 900, ink);
	context.textAlign = 'right';
	drawText(context, 'oh-my-health-data.com', width - inset, 1226, 32, 700, ink);

	const blob = await new Promise<Blob>((resolve, reject) => {
		canvas.toBlob((result) => {
			if (result) {
				resolve(result);
			} else {
				reject(new Error('포스터 이미지를 저장하지 못했습니다. 다시 시도해 주세요.'));
			}
		}, 'image/png');
	});

	const objectUrl = URL.createObjectURL(blob);
	const anchor = document.createElement('a');
	anchor.href = objectUrl;
	anchor.download = `oh-my-health-data-${theme}.png`;
	anchor.style.display = 'none';
	try {
		document.body.appendChild(anchor);
		anchor.click();
	} finally {
		anchor.remove();
		// Keep the URL alive until the browser has started handling the download.
		window.setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
	}
}
