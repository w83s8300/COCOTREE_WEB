import { ref, onBeforeUnmount } from 'vue'

/**
 * Composable for adding mouse drag/swipe support to Bootstrap Carousel.
 * Replaces the identical copy-pasted swipe logic in Home.vue, Gallery.vue, and Venue.vue.
 *
 * @param {import('vue').Ref<HTMLElement>} carouselElRef - Template ref to the carousel DOM element
 * @param {import('vue').Ref} carouselInstance - Ref holding the Bootstrap Carousel instance
 * @returns {{ setupSwipe: Function, cleanupSwipe: Function }}
 *
 * @example
 * const heroCarousel = ref(null)
 * const carousel = ref(null)
 * const { setupSwipe } = useCarouselSwipe(heroCarousel, carousel)
 * onMounted(() => {
 *   carousel.value = new Carousel(heroCarousel.value)
 *   setupSwipe()
 * })
 */
export function useCarouselSwipe(carouselElRef, carouselInstance) {
  const startX = ref(0)
  const isSwiping = ref(false)

  function handleMouseDown(e) {
    startX.value = e.pageX
    isSwiping.value = true
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
  }

  function handleMouseMove(e) {
    if (!isSwiping.value) return
    e.preventDefault()
  }

  function handleMouseUp(e) {
    if (!isSwiping.value) return
    isSwiping.value = false
    const diffX = e.pageX - startX.value

    if (diffX > 50) {
      carouselInstance.value?.prev()
    } else if (diffX < -50) {
      carouselInstance.value?.next()
    }
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  /** Attach mousedown listener to carousel element. Call in onMounted. */
  function setupSwipe() {
    const el = carouselElRef.value
    if (el) {
      el.addEventListener('mousedown', handleMouseDown)
    }
  }

  /** Remove all event listeners. Automatically called in onBeforeUnmount. */
  function cleanupSwipe() {
    const el = carouselElRef.value
    if (el) {
      el.removeEventListener('mousedown', handleMouseDown)
    }
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  onBeforeUnmount(cleanupSwipe)

  return { setupSwipe, cleanupSwipe }
}

