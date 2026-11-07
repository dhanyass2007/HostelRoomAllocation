
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models import Count
from django.views.decorators.http import require_POST

from .models import Block, Room, StudentProfile, Allocation
from .forms import BlockForm, RoomForm, StudentRegistrationForm


# -----------------------------------------
# HOME PAGE
# -----------------------------------------

def home(request):
    return render(request, 'allocation/home.html')


# -----------------------------------------
# ADMIN CHECK
# -----------------------------------------

def admin_required(view_func):
    return user_passes_test(
        lambda user: user.is_authenticated and user.is_staff
    )(view_func)


# -----------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------

@login_required
@admin_required
def admin_dashboard(request):

    total_blocks = Block.objects.count()

    total_rooms = Room.objects.count()

    total_students = StudentProfile.objects.count()

    total_capacity = sum(
        Room.objects.values_list('capacity', flat=True)
    )

    total_occupied = Allocation.objects.filter(
        status='APPROVED'
    ).count()

    total_vacancies = max(
        0, total_capacity - total_occupied
    )

    pending_requests = Allocation.objects.filter(
        status='PENDING'
    ).count()

    context = {
        'total_blocks': total_blocks,
        'total_rooms': total_rooms,
        'total_students': total_students,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'total_vacancies': total_vacancies,
        'pending_requests': pending_requests,
    }

    return render(
        request,
        'allocation/admin_dashboard.html',
        context
    )


# -----------------------------------------
# BLOCK LIST
# -----------------------------------------

@login_required
@admin_required
def block_list(request):

    blocks = Block.objects.annotate(
        room_count=Count('rooms')
    )

    return render(
        request,
        'allocation/block_list.html',
        {'blocks': blocks}
    )


# -----------------------------------------
# ADD BLOCK
# -----------------------------------------

@login_required
@admin_required
def block_add(request):

    if request.method == 'POST':

        form = BlockForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Block added successfully!'
            )

            return redirect('block_list')

    else:
        form = BlockForm()

    return render(
        request,
        'allocation/block_form.html',
        {
            'form': form,
            'title': 'Add Block'
        }
    )


# -----------------------------------------
# EDIT BLOCK
# -----------------------------------------

@login_required
@admin_required
def block_edit(request, pk):

    block = get_object_or_404(Block, pk=pk)

    if request.method == 'POST':

        form = BlockForm(request.POST, instance=block)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Block updated successfully!'
            )

            return redirect('block_list')

    else:
        form = BlockForm(instance=block)

    return render(
        request,
        'allocation/block_form.html',
        {
            'form': form,
            'title': 'Edit Block'
        }
    )


# -----------------------------------------
# DELETE BLOCK
# -----------------------------------------

@login_required
@admin_required
def block_delete(request, pk):

    block = get_object_or_404(Block, pk=pk)

    if request.method == 'POST':

        block.delete()

        messages.success(
            request,
            'Block deleted successfully!'
        )

        return redirect('block_list')

    return render(
        request,
        'allocation/confirm_delete.html',
        {
            'object': block,
            'type': 'block'
        }
    )


# -----------------------------------------
# ROOM LIST
# -----------------------------------------

@login_required
@admin_required
def room_list(request):

    rooms = Room.objects.select_related(
        'block'
    ).all().order_by('block__block_name', 'room_number')

    return render(
        request,
        'allocation/room_list.html',
        {'rooms': rooms}
    )


# -----------------------------------------
# ADD ROOM
# -----------------------------------------

@login_required
@admin_required
def room_add(request):

    if request.method == 'POST':

        form = RoomForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Room added successfully!'
            )

            return redirect('room_list')

    else:
        form = RoomForm()

    return render(
        request,
        'allocation/room_form.html',
        {
            'form': form,
            'title': 'Add Room'
        }
    )


# -----------------------------------------
# EDIT ROOM
# -----------------------------------------

@login_required
@admin_required
def room_edit(request, pk):

    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':

        form = RoomForm(request.POST, instance=room)

        if form.is_valid():

            new_capacity = form.cleaned_data['capacity']

            if new_capacity < room.occupied:

                messages.error(
                    request,
                    'Capacity cannot be less than occupied beds.'
                )

            else:

                form.save()

                messages.success(
                    request,
                    'Room updated successfully!'
                )

                return redirect('room_list')

    else:
        form = RoomForm(instance=room)

    return render(
        request,
        'allocation/room_form.html',
        {
            'form': form,
            'title': 'Edit Room'
        }
    )


# -----------------------------------------
# DELETE ROOM
# -----------------------------------------

@login_required
@admin_required
def room_delete(request, pk):

    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':

        if room.occupied > 0:

            messages.error(
                request,
                'Cannot delete a room with approved students.'
            )

            return redirect('room_list')

        room.delete()

        messages.success(
            request,
            'Room deleted successfully!'
        )

        return redirect('room_list')

    return render(
        request,
        'allocation/confirm_delete.html',
        {
            'object': room,
            'type': 'room'
        }
    )


# -----------------------------------------
# STUDENT REGISTRATION
# -----------------------------------------

def register(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = StudentRegistrationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            messages.success(
                request,
                'Registration completed successfully!'
            )

            return redirect('student_dashboard')

    else:
        form = StudentRegistrationForm()

    return render(
        request,
        'allocation/register.html',
        {'form': form}
    )


# -----------------------------------------
# STUDENT DASHBOARD
# -----------------------------------------

@login_required
def student_dashboard(request):

    if request.user.is_staff:
        return redirect('admin_dashboard')

    profile = get_object_or_404(
        StudentProfile,
        user=request.user
    )

    rooms = Room.objects.select_related(
        'block'
    ).all()

    allocations = Allocation.objects.filter(
        student=request.user
    ).select_related(
        'room',
        'room__block'
    ).order_by('-requested_date')

    return render(
        request,
        'allocation/student_dashboard.html',
        {
            'profile': profile,
            'rooms': rooms,
            'allocations': allocations,
        }
    )


# -----------------------------------------
# STUDENT ROOM REQUEST
# -----------------------------------------

@login_required
@require_POST
def room_request(request, pk):

    if request.user.is_staff:
        messages.error(request, 'Admin cannot request a student room.')
        return redirect('admin_dashboard')

    room = get_object_or_404(Room, pk=pk)

    existing = Allocation.objects.filter(
        student=request.user,
        status__in=['PENDING', 'APPROVED']
    ).exists()

    if existing:

        messages.warning(
            request,
            'You already have a pending or approved room allocation.'
        )

        return redirect('student_dashboard')

    with transaction.atomic():

        locked_room = Room.objects.select_for_update().get(pk=room.pk)

        if locked_room.vacancies <= 0:

            messages.error(
                request,
                'Sorry! This room is full.'
            )

        else:

            Allocation.objects.create(
                student=request.user,
                room=locked_room,
                status='PENDING'
            )

            messages.success(
                request,
                'Room request submitted successfully!'
            )

    return redirect('student_dashboard')


# -----------------------------------------
# ADMIN ALLOCATION REQUESTS
# -----------------------------------------

@login_required
@admin_required
def allocation_requests(request):

    allocations = Allocation.objects.select_related(
        'student',
        'room',
        'room__block'
    ).order_by('-requested_date')

    return render(
        request,
        'allocation/allocation_requests.html',
        {'allocations': allocations}
    )


# -----------------------------------------
# APPROVE / REJECT REQUEST
# -----------------------------------------

@login_required
@admin_required
@require_POST
def allocation_action(request, pk, action):

    if action not in ['approve', 'reject']:
        messages.error(request, 'Invalid action.')
        return redirect('allocation_requests')

    with transaction.atomic():

        allocation = get_object_or_404(
            Allocation.objects.select_for_update(),
            pk=pk
        )

        if allocation.status != 'PENDING':

            messages.warning(
                request,
                'This request has already been processed.'
            )

            return redirect('allocation_requests')

        if action == 'approve':

            room = Room.objects.select_for_update().get(
                pk=allocation.room_id
            )

            already_allocated = Allocation.objects.filter(
                student=allocation.student,
                status='APPROVED'
            ).exclude(pk=allocation.pk).exists()

            if already_allocated:

                messages.error(
                    request,
                    'Student already has an approved room.'
                )

            elif room.vacancies <= 0:

                messages.error(
                    request,
                    'This room has no vacancies.'
                )

            else:

                allocation.status = 'APPROVED'
                allocation.save(update_fields=['status'])

                messages.success(
                    request,
                    'Room request approved successfully!'
                )

        else:

            allocation.status = 'REJECTED'

            allocation.save(update_fields=['status'])

            messages.success(
                request,
                'Room request rejected successfully!'
            )

    return redirect('allocation_requests')
