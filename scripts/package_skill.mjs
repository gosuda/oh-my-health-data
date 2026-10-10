#!/usr/bin/env node
import { lstat, mkdir, readFile, realpath, rename, unlink, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const publicFiles = [
  'SKILL.md',
  'agents/openai.yaml',
  'assets/templates.json',
  'references/evidence.md',
  'references/portals.md',
  'references/replies.md',
  'scripts/create_case.py'
];
const uint32Max = 0xffffffff;
const crcTable = Array.from({ length: 256 }, (_, index) => {
  let value = index;
  for (let bit = 0; bit < 8; bit++) value = (value >>> 1) ^ (value & 1 ? 0xedb88320 : 0);
  return value >>> 0;
});

function crc32(buffer) {
  let crc = uint32Max;
  for (const byte of buffer) crc = (crc >>> 8) ^ crcTable[(crc ^ byte) & 0xff];
  return (crc ^ uint32Max) >>> 0;
}

function requireZip32(value, label, max = uint32Max) {
  if (!Number.isSafeInteger(value) || value < 0 || value > max) {
    throw new Error(`${label} exceeds the supported ZIP32 limit`);
  }
}

export async function packageSkill(sourceRoot, outputPath) {
  const source = await realpath(sourceRoot);
  const destination = path.resolve(outputPath);
  if (destination === source || destination.startsWith(`${source}${path.sep}`)) {
    throw new Error('The download archive must be outside the source skill directory');
  }
  const localEntries = [];
  const centralEntries = [];
  let localOffset = 0;

  // Deliberately read only these public paths. Never walk the skill directory.
  for (const relativePath of publicFiles) {
    const sourcePath = path.join(source, relativePath);
    const info = await lstat(sourcePath);
    const resolvedFile = await realpath(sourcePath);
    if (!info.isFile() || !resolvedFile.startsWith(`${source}${path.sep}`)) {
      throw new Error(`Public bundle member must be a regular file inside the skill: ${relativePath}`);
    }
    requireZip32(info.size, 'File size');
    const data = await readFile(sourcePath);
    requireZip32(data.length, 'File size');
    const filename = Buffer.from(`mma-health-data/${relativePath}`, 'utf8');
    requireZip32(filename.length, 'Filename length', 0xffff);
    const checksum = crc32(data);

    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0);
    local.writeUInt16LE(20, 4);
    local.writeUInt16LE(0x0800, 6); // UTF-8; uncompressed storage method 0.
    local.writeUInt16LE(0x0021, 12); // DOS date 1980-01-01; fixed time 00:00.
    local.writeUInt32LE(checksum, 14);
    local.writeUInt32LE(data.length, 18);
    local.writeUInt32LE(data.length, 22);
    local.writeUInt16LE(filename.length, 26);

    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0);
    central.writeUInt16LE(0x0314, 4); // Unix attributes, ZIP version 2.0.
    central.writeUInt16LE(20, 6);
    central.writeUInt16LE(0x0800, 8);
    central.writeUInt16LE(0x0021, 14);
    central.writeUInt32LE(checksum, 16);
    central.writeUInt32LE(data.length, 20);
    central.writeUInt32LE(data.length, 24);
    central.writeUInt16LE(filename.length, 28);
    central.writeUInt32LE((0o100644 << 16) >>> 0, 38);
    central.writeUInt32LE(localOffset, 42);
    localEntries.push(local, filename, data);
    centralEntries.push(central, filename);
    localOffset += local.length + filename.length + data.length;
    requireZip32(localOffset, 'Archive offset');
  }

  const centralSize = centralEntries.reduce((size, entry) => size + entry.length, 0);
  requireZip32(centralSize, 'Central directory size');
  requireZip32(publicFiles.length, 'Entry count', 0xffff);
  requireZip32(localOffset + centralSize + 22, 'Archive size');
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0);
  end.writeUInt16LE(publicFiles.length, 8);
  end.writeUInt16LE(publicFiles.length, 10);
  end.writeUInt32LE(centralSize, 12);
  end.writeUInt32LE(localOffset, 16);
  const archive = Buffer.concat([...localEntries, ...centralEntries, end]);

  await mkdir(path.dirname(destination), { recursive: true });
  const temporary = `${destination}.tmp-${process.pid}`;
  await writeFile(temporary, archive, { flag: 'wx' });
  try {
    await rename(temporary, destination);
  } catch (error) {
    await unlink(temporary);
    throw error;
  }
  return { fileCount: publicFiles.length, bytes: archive.length, output: destination };
}

async function main() {
  let source = path.join(projectRoot, 'skills/mma-health-data');
  let output = path.join(projectRoot, 'static/downloads/mma-health-data.zip');
  const args = process.argv.slice(2);
  for (let index = 0; index < args.length; index += 2) {
    if (!args[index + 1] || !['--source-root', '--output'].includes(args[index])) {
      throw new Error('Usage: node scripts/package_skill.mjs [--source-root PATH] [--output PATH]');
    }
    if (args[index] === '--source-root') source = path.resolve(args[index + 1]);
    else output = path.resolve(args[index + 1]);
  }
  const result = await packageSkill(source, output);
  console.log(`Packaged ${result.fileCount} public skill files (${result.bytes} bytes): ${result.output}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => {
    console.error(`Skill packaging failed: ${error.message}`);
    process.exitCode = 1;
  });
}
