package com.pyneon.academy.data

import org.json.JSONArray
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 复习调度（SM-2 变体）单测。
 *
 * 为什么重要：复习间隔决定「什么时候该复习」，算错了会让用户要么被过度打扰、
 * 要么错过复习时机。这里有明确的数值边界，必须锁定。
 */
class ReviewSchedulerTest {

    private fun card(
        ease: Float = 2.5f,
        interval: Int = 0,
        reps: Int = 0,
        lapses: Int = 0
    ) = object : ReviewScheduler.SchedulableCard {
        override val difficulty = ease
        override val interval = interval
        override val repetitions = reps
        override val lapses = lapses
    }

    private fun schedule(c: ReviewScheduler.SchedulableCard, q: Int) =
        kotlinx.coroutines.runBlocking { ReviewScheduler.schedule(c, q) }

    @Test
    fun `first good review schedules one day`() {
        val r = schedule(card(), 2)
        assertEquals(1, r.newInterval)
        assertEquals(1, r.newRepetitions)
    }

    @Test
    fun `second good review schedules six days`() {
        val r = schedule(card(reps = 1, interval = 1), 2)
        assertEquals(6, r.newInterval)
        assertEquals(2, r.newRepetitions)
    }

    @Test
    fun `third good review multiplies by ease`() {
        val r = schedule(card(reps = 2, interval = 6, ease = 2.5f), 2)
        assertEquals(15, r.newInterval)  // 6 * 2.5
    }

    @Test
    fun `again resets interval and counts a lapse`() {
        val r = schedule(card(reps = 3, interval = 20, lapses = 1), 0)
        assertEquals(0, r.newInterval)
        assertEquals(0, r.newRepetitions)
        assertEquals(2, r.lapses)
    }

    @Test
    fun `ease never drops below minimum`() {
        var c: ReviewScheduler.SchedulableCard = card(ease = 1.3f, reps = 2, interval = 10)
        repeat(5) {
            val r = schedule(c, 0)
            c = object : ReviewScheduler.SchedulableCard {
                override val difficulty = r.newEase
                override val interval = r.newInterval
                override val repetitions = r.newRepetitions
                override val lapses = r.lapses
            }
            assertTrue("ease 不应低于 1.3，实际 ${r.newEase}", r.newEase >= 1.3f)
        }
    }

    @Test
    fun `interval is capped at one year`() {
        val r = schedule(card(reps = 10, interval = 400, ease = 2.5f), 2)
        assertTrue("间隔不应超过 365 天，实际 ${r.newInterval}", r.newInterval <= 365)
    }

    @Test
    fun `easy increases ease`() {
        val r = schedule(card(ease = 2.5f, reps = 2, interval = 10), 3)
        assertTrue("easy 应提高 ease", r.newEase > 2.5f)
    }

    @Test
    fun `hard decreases ease but keeps progress`() {
        val r = schedule(card(ease = 2.5f, reps = 2, interval = 10), 1)
        assertTrue("hard 应降低 ease", r.newEase < 2.5f)
        assertEquals(3, r.newRepetitions)
        assertTrue("hard 仍应推进间隔", r.newInterval > 0)
    }

    @Test
    fun `next review date is in the future`() {
        val now = 1_700_000_000_000L
        val r = kotlinx.coroutines.runBlocking {
            ReviewScheduler.schedule(card(), 2, now)
        }
        assertTrue("下次复习时间应晚于当前", r.nextReviewDate > now)
    }
}
