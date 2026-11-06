package com.pyneon.academy.data

import com.pyneon.academy.utils.UpdateChecker
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * UpdateChecker 语义化版本比较的边界测试。
 *
 * 判错方向的两个后果：
 *   误报新版本 → 用户白跑一趟下载，信任受损；
 *   漏报新版本 → 用户永远停在旧版本，收不到修复。
 */
class VersionCompareTest {

    private fun newer(a: String, b: String) = UpdateChecker.isNewer(a, b)

    @Test
    fun `patch bump detected`() {
        assertTrue(newer("0.6.1", "0.6.0"))
        assertTrue(newer("v0.6.1", "0.6.0"))
    }

    @Test
    fun `minor bump beats any patch`() {
        assertTrue(newer("0.7.0", "0.6.9"))
        assertTrue(newer("0.10.0", "0.9.9"))
    }

    @Test
    fun `major bump beats everything`() {
        assertTrue(newer("1.0.0", "0.99.99"))
    }

    @Test
    fun `same version is not newer`() {
        assertTrue(!newer("0.6.0", "0.6.0"))
        assertTrue(!newer("v0.6.0", "0.6.0"))
    }

    @Test
    fun `older is not newer`() {
        assertTrue(!newer("0.5.9", "0.6.0"))
        assertTrue(!newer("0.5", "0.6.0"))
    }

    @Test
    fun `missing segments compare as zero`() {
        // "0.7" 应视为 0.7.0
        assertTrue(newer("0.7", "0.6.9"))
        assertTrue(!newer("0.6", "0.6.0"))
    }

    @Test
    fun `garbage never claims update`() {
        assertTrue(!newer("", "0.6.0"))
        assertTrue(!newer("latest", "0.6.0"))
        assertTrue(!newer("v", "0.6.0"))
        assertTrue(!newer("0.6.x", "0.6.0"))
        assertTrue(!newer("0.6.0-beta", "0.6.0"))
    }

    @Test
    fun `current garbage is also rejected`() {
        // 当前版本解析失败时，宁可漏报也不误报
        assertTrue(!newer("0.7.0", ""))
        assertTrue(!newer("0.7.0", "dev"))
    }

    @Test
    fun `leading zeros are tolerated`() {
        assertTrue(newer("v00.007.001", "0.6.9"))
        assertTrue(!newer("0.6.0", "v00.006.000"))
    }
}
