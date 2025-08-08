<template>
  <div class="instructors-page">
    <!-- 1. Banner -->
    <div class="banner">
      <img src="https://picsum.photos/1920/500?random=14" alt="Instructors Banner" class="banner-img">
      <div class="banner-text">
        <h1>師資團隊 / INSTRUCTORS</h1>
      </div>
    </div>

    <!-- 2. Instructors Grid -->
    <div class="container my-5">
      <div class="row">
        <!-- Instructor 1 -->
        <div class="col-12 col-sm-6 col-md-4 mb-4" v-for="(event, index) in events" :key="index">
          <div class="card instructor-card">
            <img :src="event.image" class="card-img-top" :alt="event.title">
            <div class="card-body">
              <h5 class="card-title">{{ event.title }}</h5>
              <p class="card-text">{{ event.shortDescription }}</p>
              <!-- <a href="#" class="btn btn-outline-dark btn-sm">View Profile</a> -->
              <button type="button" class="btn btn-outline-dark btn-sm" data-bs-toggle="modal"
                data-bs-target="#eventInstructorsModal" @click="showEventDetail(event)">
                View Profile
              </button>
            </div>
          </div>
        </div>

        <!-- Add more instructors as needed -->
      </div>
    </div>
  </div>
  <!-- Modal -->
  <div class="modal fade" id="eventInstructorsModal" tabindex="-1" aria-labelledby="eventInstructorsModalLabel"
    aria-hidden="true">
    <div class="modal-dialog modal-xl">
      <div class="modal-content ">
        <div class="modal-header">
          <h5 class="modal-title" id="eventInstructorsModalLabel">{{ selectedEvent.title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="container-fluid">
            <div class="row">
              <div class="col-12 col-sm-6 col-md-4">
                <img :src="selectedEvent.image" class="card-img-top" :alt="selectedEvent.title">
              </div>
              <div class="col-12 col-sm-6 col-md-8">
                <p>{{ selectedEvent.fullContent }}</p>
              </div>
            </div>
          </div>

        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'Instructors',
  props: {
    events: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedNews: {},
      selectedEvent: {},
      carousel: null,
      startX: 0,
      isSwiping: false,
      events: [
        {
          title: 'Teacher A',
          shortDescription: 'Hip Hop / Locking',
          fullContent: 'Teacher A is an expert in Hip Hop and Locking styles. They have participated in numerous competitions and workshops worldwide, bringing a wealth of knowledge to our studio.',
          image: 'https://picsum.photos/600/400?random=5',
        },
        {
          title: 'Teacher B',
          shortDescription: 'Ballet / Contemporary',
          fullContent: 'Teacher B specializes in Ballet and Contemporary dance, having trained at prestigious institutions. Their teaching style emphasizes technique and artistry, helping students to express themselves through movement.',
          image: 'https://picsum.photos/600/400?random=6',
        },
        {
          title: 'Teacher C',
          shortDescription: 'Jazz / Tap',
          fullContent: 'Teacher C brings a unique blend of Jazz and Tap dance to our studio. With a background in musical theater, they focus on rhythm and performance, encouraging students to find their own style while mastering the fundamentals.',
          image: 'https://picsum.photos/600/400?random=7',
        },
      ],
    };
  },
  methods: {
    showEventDetail(event) {
      this.selectedEvent = event;
      const eventInstructorsModal = new Modal(document.getElementById('eventInstructorsModal'));
      eventInstructorsModal.show();
    },
  },
};
</script>

<style src="../assets/css/Instructors.css"></style>