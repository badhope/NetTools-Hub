import { describe, it, expect } from 'vitest';
import {
  getAllProjects,
  getProjectsByKind,
  getProjectsByKindPlatform,
  getKindCounts,
  isValidKind,
  isValidPlatform,
} from './projects';
import type { ProjectKind, ProjectPlatform } from '@/types/project';

describe('projects', () => {
  describe('getAllProjects()', () => {
    it('returns all projects', () => {
      const projects = getAllProjects();
      expect(projects).toBeDefined();
      expect(Array.isArray(projects)).toBe(true);
      expect(projects.length).toBeGreaterThan(0);
    });

    it('returns projects with required fields', () => {
      const projects = getAllProjects();
      const project = projects[0];
      expect(project).toBeDefined();
      if (!project) return;
      expect(project.id).toBeDefined();
      expect(project.name).toBeDefined();
      expect(project.kind).toBeDefined();
      expect(project.platform).toBeDefined();
      expect(Array.isArray(project.platform)).toBe(true);
    });
  });

  describe('getProjectsByKind()', () => {
    it('returns projects for valid kind', () => {
      const proxyProjects = getProjectsByKind('proxy');
      expect(proxyProjects).toBeDefined();
      expect(Array.isArray(proxyProjects)).toBe(true);
      expect(proxyProjects.length).toBeGreaterThan(0);
    });

    it('returns empty array for kind with no projects', () => {
      // Assuming 'invalid_kind' doesn't exist
      const result = getProjectsByKind('invalid_kind' as ProjectKind);
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(0);
    });

    it('all returned projects have the specified kind', () => {
      const kind: ProjectKind = 'vpn';
      const projects = getProjectsByKind(kind);
      projects.forEach((project) => {
        expect(project.kind).toBe(kind);
      });
    });
  });

  describe('getProjectsByKindPlatform()', () => {
    it('returns projects for valid kind and platform', () => {
      const projects = getProjectsByKindPlatform('proxy', 'desktop');
      expect(projects).toBeDefined();
      expect(Array.isArray(projects)).toBe(true);
    });

    it('returns empty array for invalid combination', () => {
      const result = getProjectsByKindPlatform(
        'invalid' as ProjectKind,
        'invalid' as ProjectPlatform,
      );
      expect(result).toBeDefined();
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(0);
    });

    it('all returned projects support the specified platform', () => {
      const kind: ProjectKind = 'dns';
      const platform: ProjectPlatform = 'server';
      const projects = getProjectsByKindPlatform(kind, platform);
      projects.forEach((project) => {
        expect(project.kind).toBe(kind);
        expect(project.platform).toContain(platform);
      });
    });
  });

  describe('getKindCounts()', () => {
    it('returns an object with kind counts', () => {
      const counts = getKindCounts();
      expect(counts).toBeDefined();
      expect(typeof counts).toBe('object');
    });

    it('counts are non-negative numbers', () => {
      const counts = getKindCounts();
      Object.values(counts).forEach((count) => {
        expect(typeof count).toBe('number');
        expect(count).toBeGreaterThanOrEqual(0);
      });
    });

    it('total count matches getAllProjects length', () => {
      const counts = getKindCounts();
      const totalFromCounts = Object.values(counts).reduce((sum, count) => sum + count, 0);
      const allProjects = getAllProjects();
      expect(totalFromCounts).toBe(allProjects.length);
    });
  });

  describe('isValidKind()', () => {
    it('returns true for valid kinds', () => {
      const validKinds: ProjectKind[] = [
        'proxy',
        'vpn',
        'dns',
        'acceleration',
        'security',
        'monitoring',
        'ops',
        'tools',
      ];
      validKinds.forEach((kind) => {
        expect(isValidKind(kind)).toBe(true);
      });
    });

    it('returns false for invalid kinds', () => {
      expect(isValidKind('invalid')).toBe(false);
      expect(isValidKind('')).toBe(false);
      expect(isValidKind('PROXY')).toBe(false);
    });
  });

  describe('isValidPlatform()', () => {
    it('returns true for valid platforms', () => {
      const validPlatforms: ProjectPlatform[] = [
        'desktop',
        'mobile',
        'cli',
        'server',
        'browser',
        'router',
      ];
      validPlatforms.forEach((platform) => {
        expect(isValidPlatform(platform)).toBe(true);
      });
    });

    it('returns false for invalid platforms', () => {
      expect(isValidPlatform('invalid')).toBe(false);
      expect(isValidPlatform('')).toBe(false);
      expect(isValidPlatform('DESKTOP')).toBe(false);
    });
  });
});
