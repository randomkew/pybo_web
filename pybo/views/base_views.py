from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from ..models import Question, Answer, QuestionCount


def index(request):
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:  # recent
        question_list = Question.objects.order_by('-create_date')

    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}
    return render(request, 'pybo/question_list.html', context)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def detail(request, question_id):
    """
    pybo 내용 출력
    """
    page = request.GET.get('page', '1')  # 페이지
    so = request.GET.get('so', 'recent')  # 정렬기준
    question = get_object_or_404(Question, pk=question_id)
    if so == 'recommend':
        answer_list = Answer.objects.filter(question=question) \
            .annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'recent':
        answer_list = Answer.objects.filter(question=question).order_by('-create_date')

        # 페이징처리
    paginator = Paginator(answer_list, 5)  # 페이지당 5개식 보여주기
    page_obj = paginator.get_page(page)
    context = {'question': question, 'answer_set': page_obj, 'page': page, 'so': so}

    ip = get_client_ip(request)
    cnt = QuestionCount.objects.filter(ip=ip, question=question).count()
    if cnt == 0:
        qc = QuestionCount(ip=ip, question=question)
        qc.save()
        if question.hits:
            question.hits += 1
        else:
            question.hits = 1
        question.save()
    return render(request, 'pybo/question_detail.html', context)


