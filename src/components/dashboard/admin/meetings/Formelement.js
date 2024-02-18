import React from 'react'
import departmentOptions from "../../../../data/departmentOptions.json";

export default function Formelement({currmeeting, handletitle,handledate, handletime,handleattendees,handleDescription,formValid,handleBranch,handleAllBranchesChange}) {

  const handleButtonClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div>
      <div className="modal-body">
        {formValid ? null : <div className="alert alert-danger">Please fill out all the details!</div>}
        <div className="form-group">
            <label htmlFor="meetingTitle">Title</label>
            <input type="text" value = {currmeeting.title} onChange={handletitle} className="form-control" id="meetingTitle" placeholder="Enter meeting title" />
        </div>
        <div className="form-group">
            <label htmlFor="meetingDate">Date</label>
            <input type="date" value = {currmeeting.date} onChange={handledate} min={new Date().toISOString().split('T')[0]} className="form-control" id="meetingDate" />
        </div>
        <div className="form-group mb-3">
            <label htmlFor="meetingTime">Time</label>
            <input type="time" value = {currmeeting.time} onChange = {handletime} min={new Date().toTimeString().slice(0, 5)} className="form-control" id="meetingTime" />
        </div>

        <div className="accordion mb-2" id="accordionExample">
          <div className="accordion-item">
            <h2 className="accordion-header">
              <button className="accordion-button btn-sm collapsed" onClick = {handleButtonClick} type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                Attendees
              </button>
            </h2>
            <div id="collapseOne" className="accordion-collapse collapse" data-bs-parent="#accordionExample">
              <div className="accordion-body" >
                <div className="form-check">
                  <input className="form-check-input" onChange = {handleattendees} checked = {currmeeting.attendee.includes('Mentors')} type="checkbox" value="Mentors" id="mentorCheck" />
                  <label className="form-check-label" htmlFor="mentorCheck">
                    Mentors
                  </label>
                </div>

                {currmeeting.attendee.includes('Mentors') && (
                  <div className="form-group">
                    <label>Mentor Branches</label>

                    <div>

                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          value="allBranches"
                          id="allBranchesCheck"
                          checked={currmeeting.mentorBranches.length === Object.keys(departmentOptions).length}
                          onChange={handleAllBranchesChange}
                        />
                        <label className="form-check-label" htmlFor="allBranchesCheck">
                          All Branches
                        </label>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                      {Object.entries(departmentOptions).map(([key, label]) => (
                        <div key={key} className="form-check mx-3">
                          <input
                            className="form-check-input"
                            type="checkbox"
                            value={key}
                            id={`${key}Check`}
                            checked={currmeeting.mentorBranches.includes(key)}
                            onChange={handleBranch}
                          />
                          <label className="form-check-label" htmlFor={`${key}Check`}>
                            {label}
                          </label>
                        </div>
                      ))}
                      </div>
                    </div>
                  </div>
                )}

                <div className="form-check">
                  <input className="form-check-input" onChange={handleattendees} checked = {currmeeting.attendee.includes('Mentees')} type="checkbox" value="Mentees" id="menteeCheck" />
                  <label className="form-check-label" htmlFor="menteeCheck">
                    Mentees
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-group">
            <label htmlFor="Description">Description</label>
            <textarea type="text" style={{height: "100px"}} value = {currmeeting.description} onChange = {handleDescription} className="form-control" id="meetDescription" placeholder="Enter meeting Details" />
        </div>

      </div>
    </div>
  )
}
